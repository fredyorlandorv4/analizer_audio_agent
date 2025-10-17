
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode = True

class AudioOut(BaseModel):
    id: int
    original_filename: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    created_at: datetime
    download_url: str
    extra: Dict[str, Any] | None = None
    
    class Config:
        orm_mode = True



class AudioExtraUpdate(BaseModel):
    extra: Dict[str, Any]