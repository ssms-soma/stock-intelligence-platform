import copy
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, event, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import create_access_token
from app.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import SavedResearch, User


SNAPSHOT = {
    "ticker": "AAPL", "company_name": "Apple Inc.", "overall_view": "neutral",
    "confidence": "low", "analyst_style_summary": "A static research report.",
    "price_analysis": {"start_price": 100, "latest_price": 102, "trend": "sideways"},
    "news_sentiment_analysis": {"dominant_sentiment": "neutral", "neutral_count": 2},
    "valuation_snapshot": {"pe_ratio": None, "market_cap": 1000000},
    "market_metadata": {"currency": "USD", "currency_symbol": "$", "exchange": None},
    "bullish_signals": [], "bearish_signals": [], "risk_factors": ["Limited data"],
    "things_to_watch": [], "warnings": ["History unavailable"], "disclaimer": None,
}


class SavedResearchRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                                   poolclass=StaticPool)

        @event.listens_for(cls.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=Session, expire_on_commit=False)

        def override_get_db():
            with cls.SessionLocal() as db:
                yield db

        cls.original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)
        cls.original_secret = settings.jwt_secret_key
        settings.jwt_secret_key = "test-secret-key-with-at-least-32-bytes"

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(cls.original_overrides)
        settings.jwt_secret_key = cls.original_secret
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self):
        # Persistence must never regenerate research or reach a data provider.
        for target in (
            "app.services.research_service.ResearchService.get_research_report",
            "requests.sessions.Session.request", "yfinance.Ticker", "yfinance.download",
        ):
            guard = patch(target, side_effect=AssertionError("External calls are forbidden"))
            guard.start()
            self.addCleanup(guard.stop)
        with self.SessionLocal.begin() as db:
            db.execute(delete(User))
        self.owner, self.headers = self.create_user("owner@example.com")

    def create_user(self, email):
        with self.SessionLocal() as db:
            user = User(email=email, password_hash="test-hash")
            db.add(user)
            db.commit()
            user_id = user.id
        return user_id, {"Authorization": f"Bearer {create_access_token(user_id)}"}

    def save(self, **changes):
        payload = {"ticker": "AAPL", "content": copy.deepcopy(SNAPSHOT)}
        payload.update(changes)
        return self.client.post("/api/saved-research", headers=self.headers, json=payload)

    def test_authenticated_save_persists_content_and_jwt_owner(self):
        response = self.save()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("user_id", response.json())
        with self.SessionLocal() as db:
            item = db.get(SavedResearch, response.json()["id"])
            self.assertEqual(item.user_id, self.owner)
            self.assertEqual(item.content, SNAPSHOT)

    def test_normalizes_outer_and_snapshot_tickers(self):
        for ticker in (" aapl ", " infy.ns ", " tcs.bo "):
            with self.subTest(ticker=ticker):
                content = {**SNAPSHOT, "ticker": ticker}
                response = self.save(ticker=ticker, content=content)
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.json()["ticker"], ticker.strip().upper())
                self.assertEqual(response.json()["content"]["ticker"], ticker.strip().upper())

    def test_mismatched_ticker_is_rejected(self):
        self.assertEqual(self.save(ticker="MSFT").status_code, 422)

    def test_snapshot_ticker_can_be_missing_or_null(self):
        content = copy.deepcopy(SNAPSHOT)
        del content["ticker"]
        self.assertEqual(self.save(content=content).status_code, 201)
        content["ticker"] = None
        self.assertEqual(self.save(content=content).status_code, 201)

    def test_default_title_for_missing_blank_and_null(self):
        for extra in ({}, {"title": "  "}, {"title": None}):
            self.assertEqual(self.save(**extra).json()["title"], "Apple Inc. — Research Summary")

    def test_default_title_uses_ticker_and_bounds_company_name(self):
        for company in (None, "  "):
            self.assertEqual(self.save(content={**SNAPSHOT, "company_name": company}).json()["title"],
                             "AAPL — Research Summary")
        title = self.save(content={**SNAPSHOT, "company_name": "A" * 400}).json()["title"]
        self.assertLessEqual(len(title), 200)

    def test_custom_title_is_trimmed_and_length_validated(self):
        self.assertEqual(self.save(title="  My report  ").json()["title"], "My report")
        self.assertEqual(self.save(title="x" * 201).status_code, 422)

    def test_repeated_ticker_with_different_reports_is_allowed(self):
        first = self.save()
        second = self.save(content={**SNAPSHOT, "analyst_style_summary": "Another report."})
        self.assertEqual([first.status_code, second.status_code], [201, 201])
        self.assertNotEqual(first.json()["id"], second.json()["id"])

    def test_identical_snapshots_are_allowed(self):
        first, second = self.save(), self.save()
        self.assertEqual([first.status_code, second.status_code], [201, 201])
        self.assertNotEqual(first.json()["id"], second.json()["id"])

    def test_empty_list(self):
        response = self.client.get("/api/saved-research", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_only_own_metadata_ignores_query_owner(self):
        item = self.save().json()
        other, other_headers = self.create_user("other@example.com")
        self.client.post("/api/saved-research", headers=other_headers,
                         json={"ticker": "AAPL", "content": SNAPSHOT})
        response = self.client.get(f"/api/saved-research?user_id={other}", headers=self.headers)
        self.assertEqual([row["id"] for row in response.json()], [item["id"]])
        self.assertEqual(set(response.json()[0]), {"id", "ticker", "title", "created_at"})

    def test_newest_first_with_id_tiebreaker(self):
        ids = [self.save().json()["id"] for _ in range(3)]
        with self.SessionLocal.begin() as db:
            for index, item_id in enumerate(ids):
                db.get(SavedResearch, item_id).created_at = datetime(
                    2025 if index == 2 else 2026, 1, 1, tzinfo=timezone.utc)
        response = self.client.get("/api/saved-research", headers=self.headers)
        self.assertEqual([row["id"] for row in response.json()], [ids[1], ids[0], ids[2]])

    def test_own_detail(self):
        item = self.save().json()
        response = self.client.get(f'/api/saved-research/{item["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), item)

    def test_foreign_detail_matches_missing(self):
        item = self.save().json()
        _, headers = self.create_user("other@example.com")
        foreign = self.client.get(f'/api/saved-research/{item["id"]}', headers=headers)
        missing = self.client.get("/api/saved-research/99999", headers=headers)
        self.assertEqual([foreign.status_code, missing.status_code], [404, 404])
        self.assertEqual(foreign.json(), missing.json())

    def test_own_delete(self):
        item = self.save().json()
        response = self.client.delete(f'/api/saved-research/{item["id"]}', headers=self.headers)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        with self.SessionLocal() as db:
            self.assertIsNone(db.get(SavedResearch, item["id"]))

    def test_foreign_delete_matches_missing_and_preserves_item(self):
        item = self.save().json()
        _, headers = self.create_user("other@example.com")
        foreign = self.client.delete(f'/api/saved-research/{item["id"]}', headers=headers)
        missing = self.client.delete("/api/saved-research/99999", headers=headers)
        self.assertEqual([foreign.status_code, missing.status_code], [404, 404])
        self.assertEqual(foreign.json(), missing.json())
        with self.SessionLocal() as db:
            self.assertIsNotNone(db.get(SavedResearch, item["id"]))

    def test_all_endpoints_require_auth(self):
        for method, path in (("GET", ""), ("POST", ""), ("GET", "/1"), ("DELETE", "/1")):
            with self.subTest(method=method, path=path):
                kwargs = {"json": {"ticker": "AAPL", "content": SNAPSHOT}} if method == "POST" else {}
                self.assertEqual(self.client.request(method, f"/api/saved-research{path}", **kwargs).status_code, 401)

    def test_invalid_and_expired_tokens(self):
        expired = create_access_token(self.owner, now=datetime(2000, 1, 1, tzinfo=timezone.utc))
        for token in ("invalid", expired):
            self.assertEqual(self.client.get("/api/saved-research",
                headers={"Authorization": f"Bearer {token}"}).status_code, 401)

    def test_inactive_and_deleted_users_rejected(self):
        with self.SessionLocal.begin() as db:
            db.get(User, self.owner).is_active = False
        self.assertEqual(self.client.get("/api/saved-research", headers=self.headers).status_code, 401)
        with self.SessionLocal.begin() as db:
            db.execute(delete(User))
        self.assertEqual(self.client.get("/api/saved-research", headers=self.headers).status_code, 401)

    def test_ownership_body_field_rejected(self):
        self.assertEqual(self.save(user_id=999).status_code, 422)
        with self.SessionLocal() as db:
            self.assertIsNone(db.scalar(select(SavedResearch)))

    def test_malformed_required_structure(self):
        for change in ({"ticker": " "}, {"ticker": "x" * 33}, {"content": {}},
                       {"content": []}, {"content": None},
                       {"content": {**SNAPSHOT, "analyst_style_summary": " "}},
                       {"content": {**SNAPSHOT, "overall_view": []}},
                       {"content": {**SNAPSHOT, "company_name": 12}}):
            with self.subTest(change=change):
                self.assertEqual(self.save(**change).status_code, 422)

    def test_missing_required_create_fields(self):
        for payload in ({}, {"ticker": "AAPL"}, {"content": SNAPSHOT}):
            self.assertEqual(self.client.post("/api/saved-research", headers=self.headers,
                                             json=payload).status_code, 422)

    def test_known_sections_validate_containers(self):
        for field, value in (("price_analysis", []), ("news_sentiment_analysis", "text"),
                             ("valuation_snapshot", 1), ("market_metadata", []),
                             ("warnings", [1]), ("bullish_signals", {}),
                             ("risk_factors", "risk")):
            with self.subTest(field=field):
                self.assertEqual(self.save(content={**SNAPSHOT, field: value}).status_code, 422)

    def test_forward_compatible_fields_and_nulls_preserved(self):
        content = {**SNAPSHOT, "future_section": {"values": [1, None, "text"]},
                   "price_analysis": {"new_metric": 2}, "things_to_watch": None}
        response = self.save(content=content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["content"], content)

    def test_no_feature_specific_snapshot_size_limit(self):
        content = {**SNAPSHOT, "analyst_style_summary": "a" * (129 * 1024)}
        self.assertEqual(self.save(content=content).status_code, 201)

    def test_invalid_ids_rejected(self):
        for item_id in ("0", "-1", "abc"):
            for method in ("GET", "DELETE"):
                self.assertEqual(self.client.request(method, f"/api/saved-research/{item_id}",
                                                     headers=self.headers).status_code, 422)


if __name__ == "__main__":
    unittest.main()
