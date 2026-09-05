from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.market_utils import normalize_ticker


class WatchlistItemCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=32)

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker_field(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        normalized = normalize_ticker(value)
        if not normalized:
            raise ValueError("Ticker must not be blank.")
        return normalized


class WatchlistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    created_at: datetime
