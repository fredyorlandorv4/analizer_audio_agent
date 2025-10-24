from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# NUEVOS
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)  # ej: "admin", "editor", "viewer"
    description = Column(String, nullable=True)

class Area(Base):
    __tablename__ = "areas"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)  # ej: "ventas", "soporte", "it"
    description = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # NUEVO: referencias a rol y área
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True, index=True)

    role = relationship("Role")
    area = relationship("Area")

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

    # OPCIONAL: área del audio (si quieres etiquetar por área)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True, index=True)
    area = relationship("Area")

    user = relationship("User", back_populates="audios")

class ApiToken(Base):
    __tablename__ = "api_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)  # sha256
    name = Column(String, nullable=True)
    scopes = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
