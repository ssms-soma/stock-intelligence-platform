from fastapi import APIRouter

from app.services.company_service import CompanyService


router = APIRouter(tags=["Company"])

company_service = CompanyService()


@router.get("/company/{ticker}")
def get_company_profile(ticker: str):
    return company_service.get_company_profile(ticker)
