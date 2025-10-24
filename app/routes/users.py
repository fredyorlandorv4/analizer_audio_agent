from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import User
from ..schemas import UserOut
from ..security import require_role

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserOut])
def list_users(
    q: Optional[str] = Query(None, description="Filtro por email (contiene)"),
    db: Session = Depends(get_db),
    _admin = Depends(require_role("admin")),
):
    query = db.query(User)
    if q:
        query = query.filter(User.email.ilike(f"%{q}%"))
    return query.order_by(User.created_at.desc()).all()
