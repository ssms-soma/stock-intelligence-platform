"""ORM model registrations."""

from app.models.user import User
from app.models.watchlist_item import WatchlistItem

__all__ = ["User", "WatchlistItem"]
