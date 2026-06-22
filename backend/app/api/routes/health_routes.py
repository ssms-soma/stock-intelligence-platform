from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "AI Stock Intelligence Platform backend is running",
        "version": "0.1.0",
    }