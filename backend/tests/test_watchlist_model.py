import unittest

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import User, WatchlistItem


class WatchlistModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, class_=Session)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self):
        with self.SessionLocal.begin() as db:
            db.query(WatchlistItem).delete()
            db.query(User).delete()

    def test_table_is_registered_with_expected_columns(self):
        table = Base.metadata.tables["watchlist_items"]

        self.assertIs(WatchlistItem.__table__, table)
        self.assertEqual(
            set(table.columns.keys()),
            {"id", "user_id", "ticker", "created_at"},
        )

    def test_column_types_and_foreign_key_match_users_id(self):
        columns = WatchlistItem.__table__.columns
        user_id_foreign_key = next(iter(columns.user_id.foreign_keys))

        self.assertIsInstance(columns.id.type, Integer)
        self.assertIsInstance(columns.user_id.type, type(User.__table__.c.id.type))
        self.assertFalse(columns.user_id.nullable)
        self.assertEqual(user_id_foreign_key.target_fullname, "users.id")
        self.assertEqual(user_id_foreign_key.ondelete, "CASCADE")
        self.assertIsInstance(columns.ticker.type, String)
        self.assertEqual(columns.ticker.type.length, 32)
        self.assertFalse(columns.ticker.nullable)
        self.assertIsInstance(columns.created_at.type, DateTime)
        self.assertTrue(columns.created_at.type.timezone)
        self.assertFalse(columns.created_at.nullable)

    def test_user_and_ticker_have_named_unique_constraint(self):
        constraints = [
            constraint
            for constraint in WatchlistItem.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        ]

        self.assertEqual(len(constraints), 1)
        self.assertEqual(constraints[0].name, "uq_watchlist_items_user_id_ticker")
        self.assertEqual(
            [column.name for column in constraints[0].columns],
            ["user_id", "ticker"],
        )

    def test_database_rejects_duplicate_for_same_user(self):
        with self.SessionLocal() as db:
            user = User(email="model@example.com", password_hash="hash")
            db.add(user)
            db.commit()
            db.add(WatchlistItem(user_id=user.id, ticker="AAPL"))
            db.commit()
            db.add(WatchlistItem(user_id=user.id, ticker="AAPL"))

            with self.assertRaises(IntegrityError):
                db.commit()

            db.rollback()

    def test_relationships_are_bidirectional_and_delete_orphan(self):
        user_relationship = User.__mapper__.relationships["watchlist_items"]
        item_relationship = WatchlistItem.__mapper__.relationships["user"]

        self.assertEqual(user_relationship.back_populates, "user")
        self.assertEqual(item_relationship.back_populates, "watchlist_items")
        self.assertTrue(user_relationship.cascade.delete_orphan)
        self.assertTrue(user_relationship.passive_deletes)


if __name__ == "__main__":
    unittest.main()
