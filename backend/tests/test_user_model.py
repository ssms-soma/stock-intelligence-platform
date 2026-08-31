import unittest

from sqlalchemy import Boolean, DateTime, String

from app.db.base import Base
from app.models import User


class UserModelTests(unittest.TestCase):
    def test_users_table_is_registered_with_expected_columns(self):
        table = Base.metadata.tables["users"]

        self.assertIs(User.__table__, table)
        self.assertEqual(
            set(table.columns.keys()),
            {
                "id",
                "email",
                "password_hash",
                "display_name",
                "is_active",
                "created_at",
                "updated_at",
            },
        )

    def test_column_types_and_nullability(self):
        columns = User.__table__.columns

        self.assertTrue(columns.id.primary_key)
        self.assertFalse(columns.id.nullable)
        self.assertIsInstance(columns.email.type, String)
        self.assertEqual(columns.email.type.length, 320)
        self.assertFalse(columns.email.nullable)
        self.assertEqual(columns.password_hash.type.length, 255)
        self.assertFalse(columns.password_hash.nullable)
        self.assertEqual(columns.display_name.type.length, 100)
        self.assertTrue(columns.display_name.nullable)
        self.assertIsInstance(columns.is_active.type, Boolean)
        self.assertFalse(columns.is_active.nullable)
        self.assertIsInstance(columns.created_at.type, DateTime)
        self.assertTrue(columns.created_at.type.timezone)
        self.assertFalse(columns.created_at.nullable)
        self.assertIsInstance(columns.updated_at.type, DateTime)
        self.assertTrue(columns.updated_at.type.timezone)
        self.assertFalse(columns.updated_at.nullable)

    def test_email_has_unique_index(self):
        email_indexes = [
            index
            for index in User.__table__.indexes
            if list(index.columns) == [User.__table__.c.email]
        ]

        self.assertEqual(len(email_indexes), 1)
        self.assertTrue(email_indexes[0].unique)

    def test_defaults_are_configured(self):
        columns = User.__table__.columns

        self.assertIsNotNone(columns.is_active.default)
        self.assertIsNotNone(columns.is_active.server_default)
        self.assertIsNotNone(columns.created_at.default)
        self.assertIsNotNone(columns.created_at.server_default)
        self.assertIsNotNone(columns.updated_at.default)
        self.assertIsNotNone(columns.updated_at.onupdate)
        self.assertIsNotNone(columns.updated_at.server_default)


if __name__ == "__main__":
    unittest.main()
