import unittest

from sqlalchemy import JSON, DateTime, Integer, create_engine, delete, event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import SavedResearch, User


class SavedResearchModelTests(unittest.TestCase):
    def test_registered_columns_types_defaults_and_index(self):
        table = Base.metadata.tables["saved_research"]
        self.assertIs(table, SavedResearch.__table__)
        self.assertEqual(set(table.columns.keys()),
                         {"id", "user_id", "ticker", "title", "content", "created_at"})
        self.assertTrue(all(not column.nullable for column in table.columns))
        self.assertIsInstance(table.c.id.type, Integer)
        self.assertIsInstance(table.c.content.type, JSON)
        self.assertIsInstance(table.c.created_at.type, DateTime)
        self.assertTrue(table.c.created_at.type.timezone)
        self.assertIsNotNone(table.c.created_at.default)
        self.assertIsNotNone(table.c.created_at.server_default)
        self.assertEqual(table.c.ticker.type.length, 32)
        self.assertEqual(table.c.title.type.length, 200)
        index = next(iter(table.indexes))
        self.assertEqual(index.name, "ix_saved_research_user_id_created_at_id")
        self.assertEqual([column.name for column in index.columns], ["user_id", "created_at", "id"])
        self.assertFalse(index.unique)

    def test_foreign_key_and_relationships(self):
        column = SavedResearch.__table__.c.user_id
        self.assertIsInstance(column.type, type(User.__table__.c.id.type))
        foreign_key = next(iter(column.foreign_keys))
        self.assertEqual(foreign_key.target_fullname, "users.id")
        self.assertEqual(foreign_key.ondelete, "CASCADE")
        relationship = User.__mapper__.relationships["saved_research"]
        self.assertEqual(relationship.back_populates, "user")
        self.assertTrue(relationship.cascade.delete_orphan)
        self.assertTrue(relationship.passive_deletes)
        self.assertEqual(SavedResearch.__mapper__.relationships["user"].back_populates, "saved_research")

    def setUp(self):
        self.engine = create_engine("sqlite://")

        @event.listens_for(self.engine, "connect")
        def foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.addCleanup(self.engine.dispose)

    def make_item(self, db):
        user = User(email="cascade@example.com", password_hash="hash")
        item = SavedResearch(ticker="AAPL", title="Report", content={"summary": "Static"})
        user.saved_research.append(item)
        db.add(user)
        db.commit()
        return user.id, item.id

    def test_database_user_delete_cascades_with_unloaded_relationship(self):
        with Session(self.engine) as db:
            user_id, item_id = self.make_item(db)
        with Session(self.engine) as db:
            db.execute(delete(User).where(User.id == user_id))
            db.commit()
            self.assertIsNone(db.get(SavedResearch, item_id))

    def test_orm_user_delete_cascades(self):
        with Session(self.engine) as db:
            user_id, item_id = self.make_item(db)
        with Session(self.engine) as db:
            db.delete(db.get(User, user_id))
            db.commit()
            self.assertIsNone(db.get(SavedResearch, item_id))

    def test_relationship_removal_deletes_orphan(self):
        with Session(self.engine) as db:
            user_id, item_id = self.make_item(db)
            user = db.get(User, user_id)
            user.saved_research.clear()
            db.commit()
            self.assertIsNone(db.get(SavedResearch, item_id))


if __name__ == "__main__":
    unittest.main()
