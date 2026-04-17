"""
database.py — SQLAlchemy models + auth helpers (Python 3.14 / bcrypt 5.x compatible)
"""
import os
from datetime import datetime, timedelta

import bcrypt
import jwt
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# ── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY  = os.getenv("SECRET_KEY", "phishguard-super-secret-key-2024")
ALGORITHM   = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours (reduced from 7 days for security)
EMAIL_VERIFY_EXPIRE_MINUTES = 60 * 24  # 24 hours to verify email

DB_PATH = os.path.join(os.path.dirname(__file__), "phishing.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Models ────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50), unique=True, index=True, nullable=False)
    email         = Column(String(100), unique=True, index=True, nullable=True)
    password_hash = Column(String(200), nullable=False)
    is_verified   = Column(Integer, default=0)  # 0 = not verified, 1 = verified
    verification_token = Column(String(200), nullable=True)
    token_expiry  = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)


class ScanHistory(Base):
    __tablename__ = "scan_history"
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, index=True)
    url             = Column(String, nullable=False)
    prediction      = Column(String(50))
    confidence_score = Column(Float)
    risk_score      = Column(Float)
    timestamp       = Column(DateTime, default=datetime.utcnow)


# Create tables on import
Base.metadata.create_all(bind=engine)


# ── DB session dependency ─────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Password helpers (direct bcrypt — passlib is incompatible with bcrypt 5.x) ─
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT helpers ───────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

def create_verification_token(email: str) -> str:
    """Create email verification token that expires in 24 hours."""
    expire = datetime.utcnow() + timedelta(minutes=EMAIL_VERIFY_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "type": "email_verification",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_verification_token(token: str) -> dict | None:
    """Decode and validate email verification token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        return payload
    except jwt.PyJWTError:
        return None
