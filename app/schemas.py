from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    class Config: orm_mode = True

class AreaOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    class Config: orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role_id: Optional[int] = None
    area_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Optional[RoleOut] = None
    area: Optional[AreaOut] = None
    class Config: orm_mode = True

class UserUpdate(BaseModel):
    role_id: Optional[int] = None
    area_id: Optional[int] = None

# (ya tenías) AudioOut …
# Si quieres devolver area del audio:
class AudioOut(BaseModel):
    id: int
    original_filename: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    created_at: datetime
    download_url: str
    extra: Dict[str, Any] | None = None
    # opcional:
    # area: Optional[AreaOut] = None

    class Config:
        orm_mode = True

class AudioExtraUpdate(BaseModel):
    extra: Dict[str, Any]