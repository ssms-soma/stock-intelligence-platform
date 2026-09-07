"""ORM model registrations."""

from app.models.user import User
from app.models.saved_research import SavedResearch
from app.models.watchlist_item import WatchlistItem

__all__ = ["User", "WatchlistItem", "SavedResearch"]
