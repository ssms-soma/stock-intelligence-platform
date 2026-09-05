import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import create_access_token
from app.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User, WatchlistItem


class WatchlistRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(
            bind=cls.engine,
            class_=Session,
            expire_on_commit=False,
        )

        def override_get_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)
        cls.original_secret = settings.jwt_secret_key
        settings.jwt_secret_key = "test-secret-key-with-at-least-32-bytes"

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        settings.jwt_secret_key = cls.original_secret
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self):
        with self.SessionLocal.begin() as db:
            db.execute(delete(WatchlistItem))
            db.execute(delete(User))

    def create_user(self, email: str) -> tuple[User, dict[str, str]]:
        with self.SessionLocal() as db:
            user = User(email=email, password_hash="test-hash")
            db.add(user)
            db.commit()
            db.refresh(user)
            db.expunge(user)

        token = create_access_token(user.id)
        return user, {"Authorization": f"Bearer {token}"}

    def test_authenticated_user_adds_and_normalizes_ticker(self):
        user, headers = self.create_user("owner@example.com")

        response = self.client.post(
            "/api/watchlist",
            headers=headers,
            json={"ticker": " aapl "},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["ticker"], "AAPL")
        with self.SessionLocal() as db:
            item = db.scalar(select(WatchlistItem))
            self.assertEqual(item.user_id, user.id)
            self.assertEqual(item.ticker, "AAPL")

    def test_lowercase_ticker_is_normalized(self):
        _, headers = self.create_user("lowercase@example.com")

        response = self.client.post(
            "/api/watchlist", headers=headers, json={"ticker": "msft"}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["ticker"], "MSFT")

    def test_blank_ticker_is_rejected(self):
        _, headers = self.create_user("blank@example.com")

        response = self.client.post(
            "/api/watchlist", headers=headers, json={"ticker": "   "}
        )

        self.assertEqual(response.status_code, 422)

    def test_duplicate_normalized_ticker_returns_conflict_and_one_row(self):
        user, headers = self.create_user("duplicate@example.com")
        first = self.client.post(
            "/api/watchlist", headers=headers, json={"ticker": "AAPL"}
        )
        duplicate = self.client.post(
            "/api/watchlist", headers=headers, json={"ticker": " aapl "}
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(duplicate.status_code, 409)
        with self.SessionLocal() as db:
            items = db.scalars(
                select(WatchlistItem).where(WatchlistItem.user_id == user.id)
            ).all()
            self.assertEqual(len(items), 1)

    def test_same_ticker_can_belong_to_two_users(self):
        _, first_headers = self.create_user("first@example.com")
        _, second_headers = self.create_user("second@example.com")

        first = self.client.post(
            "/api/watchlist", headers=first_headers, json={"ticker": "AAPL"}
        )
        second = self.client.post(
            "/api/watchlist", headers=second_headers, json={"ticker": "AAPL"}
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)

    def test_list_returns_only_current_users_items(self):
        _, first_headers = self.create_user("list-first@example.com")
        _, second_headers = self.create_user("list-second@example.com")
        self.client.post(
            "/api/watchlist", headers=first_headers, json={"ticker": "AAPL"}
        )
        self.client.post(
            "/api/watchlist", headers=second_headers, json={"ticker": "MSFT"}
        )

        response = self.client.get("/api/watchlist", headers=first_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["ticker"] for item in response.json()], ["AAPL"])

    def test_empty_watchlist_returns_empty_list(self):
        _, headers = self.create_user("empty@example.com")

        response = self.client.get("/api/watchlist", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_user_removes_own_ticker(self):
        _, headers = self.create_user("remove@example.com")
        self.client.post(
            "/api/watchlist", headers=headers, json={"ticker": "AAPL"}
        )

        response = self.client.delete("/api/watchlist/aapl", headers=headers)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get("/api/watchlist", headers=headers).json(), [])

    def test_delete_missing_ticker_returns_not_found(self):
        _, headers = self.create_user("missing@example.com")

        response = self.client.delete("/api/watchlist/AAPL", headers=headers)

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_another_users_ticker(self):
        _, owner_headers = self.create_user("delete-owner@example.com")
        _, other_headers = self.create_user("delete-other@example.com")
        self.client.post(
            "/api/watchlist", headers=owner_headers, json={"ticker": "AAPL"}
        )

        response = self.client.delete("/api/watchlist/AAPL", headers=other_headers)

        self.assertEqual(response.status_code, 404)
        owner_items = self.client.get("/api/watchlist", headers=owner_headers)
        self.assertEqual([item["ticker"] for item in owner_items.json()], ["AAPL"])

    def test_unauthenticated_requests_are_rejected(self):
        responses = (
            self.client.get("/api/watchlist"),
            self.client.post("/api/watchlist", json={"ticker": "AAPL"}),
            self.client.delete("/api/watchlist/AAPL"),
        )

        self.assertEqual([response.status_code for response in responses], [401, 401, 401])

    def test_invalid_and_expired_tokens_are_rejected(self):
        user, _ = self.create_user("tokens@example.com")
        invalid_response = self.client.get(
            "/api/watchlist",
            headers={"Authorization": "Bearer not-a-token"},
        )
        expired_token = create_access_token(
            user.id,
            now=datetime(2000, 1, 1, tzinfo=timezone.utc),
        )
        expired_response = self.client.get(
            "/api/watchlist",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        self.assertEqual(invalid_response.status_code, 401)
        self.assertEqual(expired_response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
