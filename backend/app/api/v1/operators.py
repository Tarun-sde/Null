from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Operator
from app.schemas.operator import OperatorResponse

router = APIRouter(prefix="/operators", tags=["Operators"])


@router.get("", response_model=List[OperatorResponse])
def list_operators(db: Session = Depends(get_db)):
    """Retrieve list of all certified heavy equipment operators."""
    return db.query(Operator).all()
