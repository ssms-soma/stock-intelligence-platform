from sqlalchemy import select
from sqlalchemy.orm import Session, load_only

from app.models import SavedResearch
from app.schemas.saved_research import SavedResearchCreate
from app.utils.market_utils import normalize_ticker


class SavedResearchNotFoundError(LookupError):
    pass


class SavedResearchService:
    def __init__(self, db: Session):
        self.db = db

    def list_items(self, *, user_id: int) -> list[SavedResearch]:
        return list(self.db.scalars(
            select(SavedResearch)
            .options(load_only(SavedResearch.id, SavedResearch.ticker,
                               SavedResearch.title, SavedResearch.created_at))
            .where(SavedResearch.user_id == user_id)
            .order_by(SavedResearch.created_at.desc(), SavedResearch.id.desc())
        ))

    def add_item(self, *, user_id: int, request: SavedResearchCreate) -> SavedResearch:
        ticker = normalize_ticker(request.ticker)
        company = (request.content.company_name or "").strip() or ticker
        title = request.title or f"{company[:181]} — Research Summary"
        item = SavedResearch(
            user_id=user_id, ticker=ticker, title=title,
            content=request.content.model_dump(mode="json", exclude_unset=True),
        )
        self.db.add(item)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(item)
        return item

    def get_item(self, *, user_id: int, item_id: int) -> SavedResearch:
        item = self.db.scalar(select(SavedResearch).where(
            SavedResearch.id == item_id, SavedResearch.user_id == user_id,
        ))
        if item is None:
            raise SavedResearchNotFoundError("Saved research not found.")
        return item

    def remove_item(self, *, user_id: int, item_id: int) -> None:
        item = self.get_item(user_id=user_id, item_id=item_id)
        self.db.delete(item)
        self.db.commit()
