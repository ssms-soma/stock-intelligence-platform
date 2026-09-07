from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.saved_research import SavedResearchCreate, SavedResearchDetail, SavedResearchRead
from app.services.saved_research_service import SavedResearchNotFoundError, SavedResearchService

router = APIRouter(prefix="/saved-research", tags=["Saved Research"])
CurrentUser = Annotated[User, Depends(get_current_user)]
Database = Annotated[Session, Depends(get_db)]
ItemId = Annotated[int, Path(gt=0)]


@router.get("", response_model=list[SavedResearchRead])
def list_saved_research(current_user: CurrentUser, db: Database):
    return SavedResearchService(db).list_items(user_id=current_user.id)


@router.post("", response_model=SavedResearchDetail, status_code=201)
def save_research(request: SavedResearchCreate, current_user: CurrentUser, db: Database):
    return SavedResearchService(db).add_item(user_id=current_user.id, request=request)


@router.get("/{id}", response_model=SavedResearchDetail)
def get_saved_research(id: ItemId, current_user: CurrentUser, db: Database):
    try:
        return SavedResearchService(db).get_item(user_id=current_user.id, item_id=id)
    except SavedResearchNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/{id}", status_code=204)
def delete_saved_research(id: ItemId, current_user: CurrentUser, db: Database):
    try:
        SavedResearchService(db).remove_item(user_id=current_user.id, item_id=id)
    except SavedResearchNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return Response(status_code=204)
