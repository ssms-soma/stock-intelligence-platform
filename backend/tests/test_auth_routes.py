import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import decode_access_token
from app.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User


class AuthRoutesTests(unittest.TestCase):
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
            db.execute(delete(User))

    def register(self, email="Test@Example.COM", password="strong-password"):
        return self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": password,
                "display_name": " Test User ",
            },
        )

    def test_registration_normalizes_email_and_hides_password_hash(self):
        response = self.register(email="  Test@Example.COM  ")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "test@example.com")
        self.assertEqual(response.json()["display_name"], "Test User")
        self.assertNotIn("password", response.json())
        self.assertNotIn("password_hash", response.json())
        with self.SessionLocal() as db:
            user = db.query(User).one()
            self.assertNotEqual(user.password_hash, "strong-password")

    def test_duplicate_registration_is_rejected(self):
        self.assertEqual(self.register().status_code, 201)

        response = self.register(email=" test@example.com ")

        self.assertEqual(response.status_code, 409)

    def test_login_succeeds_and_invalid_credentials_are_generic(self):
        self.register()

        response = self.client.post(
            "/api/auth/login",
            json={"email": " TEST@example.com ", "password": "strong-password"},
        )
        invalid_response = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["token_type"], "bearer")
        self.assertGreater(decode_access_token(response.json()["access_token"]), 0)
        self.assertEqual(invalid_response.status_code, 401)
        self.assertEqual(invalid_response.json()["detail"], "Invalid email or password.")

    def test_oauth2_token_form_returns_jwt_and_rejects_invalid_credentials(self):
        self.register()

        response = self.client.post(
            "/api/auth/token",
            data={"username": " TEST@example.com ", "password": "strong-password"},
        )
        invalid_response = self.client.post(
            "/api/auth/token",
            data={"username": "test@example.com", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["token_type"], "bearer")
        self.assertGreater(decode_access_token(response.json()["access_token"]), 0)
        self.assertEqual(invalid_response.status_code, 401)
        self.assertEqual(invalid_response.json()["detail"], "Invalid email or password.")

    def test_openapi_oauth2_flow_uses_token_endpoint(self):
        security_schemes = self.client.get("/openapi.json").json()["components"][
            "securitySchemes"
        ]
        oauth2_scheme = next(iter(security_schemes.values()))

        self.assertEqual(
            oauth2_scheme["flows"]["password"]["tokenUrl"],
            "/api/auth/token",
        )

    def test_me_requires_authentication_and_returns_safe_user(self):
        registration = self.register()
        login = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "strong-password"},
        )

        missing_response = self.client.get("/api/auth/me")
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        )

        self.assertEqual(missing_response.status_code, 401)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), registration.json())
        self.assertNotIn("password_hash", response.json())

    def test_inactive_user_cannot_login_or_use_existing_token(self):
        self.register()
        login = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "strong-password"},
        )
        token = login.json()["access_token"]
        with self.SessionLocal.begin() as db:
            user = db.query(User).one()
            user.is_active = False

        login_response = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "strong-password"},
        )
        me_response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(login_response.status_code, 401)
        self.assertEqual(me_response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
