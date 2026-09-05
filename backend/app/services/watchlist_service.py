from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import WatchlistItem
from app.utils.market_utils import normalize_ticker


class DuplicateWatchlistItemError(ValueError):
    pass


class InvalidTickerError(ValueError):
    pass


class WatchlistItemNotFoundError(LookupError):
    pass


class WatchlistService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_ticker(ticker: str) -> str:
        normalized_ticker = normalize_ticker(ticker)
        if not normalized_ticker or len(normalized_ticker) > 32:
            raise InvalidTickerError("Ticker must be between 1 and 32 characters.")
        return normalized_ticker

    def list_items(self, *, user_id: int) -> list[WatchlistItem]:
        return list(
            self.db.scalars(
                select(WatchlistItem)
                .where(WatchlistItem.user_id == user_id)
                .order_by(WatchlistItem.created_at.desc(), WatchlistItem.id.desc())
            )
        )

    def add_item(self, *, user_id: int, ticker: str) -> WatchlistItem:
        normalized_ticker = self._normalize_ticker(ticker)
        existing_item = self.db.scalar(
            select(WatchlistItem).where(
                WatchlistItem.user_id == user_id,
                WatchlistItem.ticker == normalized_ticker,
            )
        )
        if existing_item is not None:
            raise DuplicateWatchlistItemError(
                "Ticker is already in your watchlist."
            )

        item = WatchlistItem(user_id=user_id, ticker=normalized_ticker)
        self.db.add(item)
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            raise DuplicateWatchlistItemError(
                "Ticker is already in your watchlist."
            ) from error

        self.db.refresh(item)
        return item

    def remove_item(self, *, user_id: int, ticker: str) -> None:
        normalized_ticker = self._normalize_ticker(ticker)
        item = self.db.scalar(
            select(WatchlistItem).where(
                WatchlistItem.user_id == user_id,
                WatchlistItem.ticker == normalized_ticker,
            )
        )
        if item is None:
            raise WatchlistItemNotFoundError(
                "Ticker is not in your watchlist."
            )

        self.db.delete(item)
        self.db.commit()
