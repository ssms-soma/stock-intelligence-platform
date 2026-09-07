from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

from app.utils.market_utils import normalize_ticker


class ResearchSnapshot(BaseModel):
    # Keep future report fields while validating the sections used by the renderer.
    model_config = ConfigDict(extra="allow", strict=True, allow_inf_nan=False)
    __pydantic_extra__: dict[str, JsonValue] = Field(init=False)

    ticker: str | None = None
    company_name: str | None = None
    overall_view: str
    analyst_style_summary: str
    confidence: str | float | None = None
    price_analysis: dict[str, JsonValue] | None = None
    news_sentiment_analysis: dict[str, JsonValue] | None = None
    valuation_snapshot: dict[str, JsonValue] | None = None
    market_metadata: dict[str, str | None] | None = None
    bullish_signals: list[str] | None = None
    bearish_signals: list[str] | None = None
    risk_factors: list[str] | None = None
    things_to_watch: list[str] | None = None
    warnings: list[str] | None = None
    disclaimer: str | None = None

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value):
        if value is None:
            return value
        value = normalize_ticker(value)
        if not value or len(value) > 32:
            raise ValueError("Ticker must be between 1 and 32 characters.")
        return value

    @field_validator("overall_view", "analyst_style_summary")
    @classmethod
    def require_text(cls, value):
        if not value.strip():
            raise ValueError("Report text must not be blank.")
        return value


class SavedResearchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticker: Annotated[str, Field(min_length=1, max_length=32)]
    title: str | None = None
    content: ResearchSnapshot

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker_field(cls, value):
        return normalize_ticker(value) if isinstance(value, str) else value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is None:
            return None
        value = value.strip()
        if len(value) > 200:
            raise ValueError("Title must be at most 200 characters.")
        return value or None

    @model_validator(mode="after")
    def consistent_ticker(self):
        if self.content.ticker is not None and self.content.ticker != self.ticker:
            raise ValueError("Snapshot ticker must match ticker.")
        return self


class SavedResearchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    title: str
    created_at: datetime


class SavedResearchDetail(SavedResearchRead):
    content: dict[str, JsonValue]
