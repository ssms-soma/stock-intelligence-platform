from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models import User, WatchlistItem
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemRead
from app.services.watchlist_service import (
    DuplicateWatchlistItemError,
    InvalidTickerError,
    WatchlistItemNotFoundError,
    WatchlistService,
)


router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get("", response_model=list[WatchlistItemRead])
def list_watchlist(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[WatchlistItem]:
    return WatchlistService(db).list_items(user_id=current_user.id)


@router.post(
    "",
    response_model=WatchlistItemRead,
    status_code=status.HTTP_201_CREATED,
)
def add_watchlist_item(
    request: WatchlistItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WatchlistItem:
    try:
        return WatchlistService(db).add_item(
            user_id=current_user.id,
            ticker=request.ticker,
        )
    except DuplicateWatchlistItemError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist_item(
    ticker: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    try:
        WatchlistService(db).remove_item(
            user_id=current_user.id,
            ticker=ticker,
        )
    except InvalidTickerError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except WatchlistItemNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)
