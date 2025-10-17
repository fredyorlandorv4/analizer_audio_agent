
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger,JSON,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    audios = relationship("Audio", back_populates="user")

class Audio(Base):
    __tablename__ = "audios"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    stored_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    webhook_url = Column(String, nullable=True)
    webhook_status = Column(String, nullable=True)  # pending|sent|failed
    webhook_response_code = Column(Integer, nullable=True)
    webhook_response_body = Column(String, nullable=True)
    extra = Column(JSON, nullable=True)  
    user = relationship("User", back_populates="audios")


class ApiToken(Base):
    __tablename__ = "api_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)  # sha256
    name = Column(String, nullable=True)           # opcional: “token iOS de Juan”
    scopes = Column(String, nullable=True)         # csv o json si prefieres
    expires_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")