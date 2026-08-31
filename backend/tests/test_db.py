import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import DeclarativeBase, Session

from app.db.base import Base
from app.db.session import SessionLocal, _require_database_url, engine, get_db


class DatabaseFoundationTests(unittest.TestCase):
    def test_base_uses_modern_declarative_base(self):
        self.assertTrue(issubclass(Base, DeclarativeBase))

    def test_engine_and_session_factory_are_configured(self):
        self.assertEqual(engine.url.drivername, "postgresql+psycopg")
        self.assertTrue(engine.pool._pre_ping)
        self.assertTrue(issubclass(SessionLocal.class_, Session))
        self.assertIs(SessionLocal.kw["bind"], engine)

    def test_missing_database_url_has_clear_error(self):
        with self.assertRaisesRegex(RuntimeError, "DATABASE_URL is required"):
            _require_database_url(None)

    def test_get_db_closes_its_session(self):
        db = MagicMock(spec=Session)

        with patch("app.db.session.SessionLocal", return_value=db):
            dependency = get_db()
            self.assertIs(next(dependency), db)
            dependency.close()

        db.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
