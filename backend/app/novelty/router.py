from fastapi import APIRouter, HTTPException

from app.novelty.schemas import NoveltyScanRequest, NoveltyScanResponse
from app.novelty.service import scan_novelty


router = APIRouter(
    prefix="/novelty",
    tags=["Novelty Scanner"],
)


@router.post("/scan", response_model=NoveltyScanResponse)
def novelty_scan(request: NoveltyScanRequest) -> NoveltyScanResponse:
    try:
        return scan_novelty(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Novelty scan failed: {exc}",
        ) from exc