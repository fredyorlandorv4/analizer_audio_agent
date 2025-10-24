from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..database import get_db
from ..models import Role
from ..security import require_role

router = APIRouter(prefix="/roles", tags=["roles"])

class RoleIn(BaseModel):
    name: str
    description: str | None = None

@router.get("", response_model=List[RoleIn])
def list_roles(db: Session = Depends(get_db), _admin = Depends(require_role("admin"))):
    return db.query(Role).order_by(Role.name.asc()).all()

@router.post("", response_model=RoleIn, status_code=201)
def create_role(payload: RoleIn, db: Session = Depends(get_db), _admin = Depends(require_role("admin"))):
    if db.query(Role).filter(Role.name == payload.name).first():
        raise HTTPException(400, "Role ya existe")
    r = Role(name=payload.name, description=payload.description)
    db.add(r); db.commit(); db.refresh(r)
    return r
