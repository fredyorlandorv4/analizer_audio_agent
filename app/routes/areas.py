from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..database import get_db
from ..models import Area
from ..security import require_role
from ..schemas import AreaOut

router = APIRouter(prefix="/areas", tags=["areas"])

class AreaIn(BaseModel):
    name: str
    description: str | None = None

@router.get("", response_model=List[AreaOut])
def list_areas(db: Session = Depends(get_db), _admin = Depends(require_role("admin"))):
    return db.query(Area).order_by(Area.name.asc()).all()

@router.post("", response_model=AreaOut, status_code=201)
def create_area(payload: AreaIn, db: Session = Depends(get_db), _admin = Depends(require_role("admin"))):
    if db.query(Area).filter(Area.name == payload.name).first():
        raise HTTPException(400, "Area ya existe")
    a = Area(name=payload.name, description=payload.description)
    db.add(a); db.commit(); db.refresh(a)
    return a
