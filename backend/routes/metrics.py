from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.metrics_service import calculate_metrics

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("")
def get_metrics(db: Session = Depends(get_db)):
    return calculate_metrics(db)
