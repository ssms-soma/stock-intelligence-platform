import unittest
from datetime import datetime, timedelta, timezone

from app.auth.security import (
    AuthConfigurationError,
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.config import settings


class AuthSecurityTests(unittest.TestCase):
    def setUp(self):
        self.original_secret = settings.jwt_secret_key
        settings.jwt_secret_key = "test-secret-key-with-at-least-32-bytes"

    def tearDown(self):
        settings.jwt_secret_key = self.original_secret

    def test_password_hashing_and_verification(self):
        password_hash = hash_password("correct horse battery staple")

        self.assertNotEqual(password_hash, "correct horse battery staple")
        self.assertTrue(password_hash.startswith("$argon2"))
        self.assertTrue(
            verify_password("correct horse battery staple", password_hash)
        )
        self.assertFalse(verify_password("wrong password", password_hash))

    def test_access_token_round_trip_and_rejection(self):
        token = create_access_token(42)

        self.assertEqual(decode_access_token(token), 42)
        with self.assertRaises(InvalidAccessTokenError):
            decode_access_token(f"{token}invalid")

    def test_expired_access_token_is_rejected(self):
        expired_token = create_access_token(
            42,
            now=datetime.now(timezone.utc)
            - timedelta(minutes=settings.jwt_access_token_expire_minutes + 1),
        )

        with self.assertRaises(InvalidAccessTokenError):
            decode_access_token(expired_token)

    def test_missing_secret_has_clear_error(self):
        settings.jwt_secret_key = None

        with self.assertRaisesRegex(AuthConfigurationError, "JWT_SECRET_KEY"):
            create_access_token(42)


if __name__ == "__main__":
    unittest.main()
