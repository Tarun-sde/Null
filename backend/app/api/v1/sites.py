from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Site
from app.schemas.site import SiteResponse

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get("", response_model=List[SiteResponse])
def list_sites(db: Session = Depends(get_db)):
    """Retrieve list of all active job sites."""
    return db.query(Site).all()
