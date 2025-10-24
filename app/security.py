
from datetime import datetime, timedelta
from hmac import compare_digest
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,HTTPBearer,HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User
from jose import jwt, JWTError

import hashlib
from datetime import datetime
from typing import Optional

from .database import get_db
from .models import ApiToken, User

# Use bcrypt_sha256 to avoid 72-byte limit.
pwd_context = CryptContext(
    schemes=["argon2"],   # sin bcrypt
    deprecated="auto",
)

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

#bearer_scheme = HTTPBearer(auto_error=True)

bearer = HTTPBearer(auto_error=True)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    print('\n\n\n\n')
    print('password value',password)
    print('\n\n\n\n\n')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()



def require_service_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    token = credentials.credentials  # <- el valor después de "Bearer "
    expected: Optional[str] = settings.SERVICE_TOKEN


    print('\n\n\n\n\n\n')
    print(token,expected)
    print('\n\n\n\n\n\n')
    if not expected:
        raise HTTPException(500, detail="SERVICE_TOKEN no está configurado")
    if not token or not compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


"""
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    raw = credentials.credentials
    if not raw:
        raise HTTPException(401, "Falta token", headers={"WWW-Authenticate": "Bearer"})
    th = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    t = db.query(ApiToken).filter(ApiToken.token_hash == th, ApiToken.revoked == False).first()
    if not t or (t.expires_at and t.expires_at < datetime.utcnow()):
        raise HTTPException(401, "Token inválido o expirado", headers={"WWW-Authenticate": "Bearer"})
    u = db.query(User).get(t.user_id)
    if not u:
        raise HTTPException(401, "Usuario no existe")
    return u"""


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    token = cred.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(401, "Token inválido")
        user = db.query(User).get(int(sub))
        if not user:
            raise HTTPException(401, "Usuario no encontrado")
        return user
    except JWTError:
        raise HTTPException(401, "Token inválido")
    

# def get_current_user_from_token(...)-> User: ...

def require_role(*allowed: str):
    def _dep(current_user: User = Depends(get_current_user)) -> User:
        r = current_user.role.name if current_user.role else None
        if not r or r not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
        return current_user
    return _dep
