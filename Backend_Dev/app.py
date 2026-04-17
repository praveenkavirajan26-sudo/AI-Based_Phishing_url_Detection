"""
app.py — FastAPI REST API for PhishGuard AI
"""
import os, sys, json, warnings
warnings.filterwarnings("ignore")

import requests as http_requests
import numpy as np
import joblib
import whois
import tldextract
import re
import urllib.parse
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional

# Local imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from database import (
    User as DBUser, ScanHistory, get_db,
    verify_password, get_password_hash,
    create_access_token, decode_access_token, TOKEN_EXPIRE_MINUTES,
    create_verification_token, decode_verification_token
)
from features import extract_features, FEATURE_NAMES
from explainer import get_shap_explanation
from rate_limiter import check_rate_limit, get_client_ip
from email_service import email_service
from advanced_detection import advanced_url_analysis

# ── Paths ─────────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(BASE_DIR, "model", "phishing_model.pkl")
META_PATH  = os.path.join(BASE_DIR, "model", "metadata.json")

_model = None
_meta  = None

def _load_model():
    global _model, _meta
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError("Model not found. Run `python train.py` first.")
        _model = joblib.load(MODEL_PATH)
    if _meta is None and os.path.exists(META_PATH):
        with open(META_PATH) as f:
            _meta = json.load(f)
    return _model, _meta


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(title="PhishGuard AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────
class URLRequest(BaseModel):
    url: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None  # Email is now optional but recommended

class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class EmailVerificationRequest(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# ── Auth helpers ──────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[DBUser]:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    return db.query(DBUser).filter(DBUser.username == username).first()


# ── Threat Intel & OSINT ──────────────────────────────────────────────────────

def get_domain_age(domain: str) -> Optional[int]:
    """Return the domain age in days, or None if it cannot be determined."""
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if not creation_date:
            return None
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(creation_date, datetime):
            age_timedelta = datetime.now() - creation_date
            return max(0, age_timedelta.days)
    except Exception:
        pass
    return None

GSB_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")

def check_safe_browsing(url: str) -> dict:
    if not GSB_API_KEY:
        return {"source": "Google Safe Browsing", "safe": True,
                "details": "API key not configured (configure GOOGLE_SAFE_BROWSING_API_KEY env var)"}
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GSB_API_KEY}"
    payload = {
        "client": {"clientId": "phishguard", "clientVersion": "2.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE","SOCIAL_ENGINEERING","UNWANTED_SOFTWARE","POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    try:
        resp = http_requests.post(api_url, json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "matches" in data:
                return {"source": "Google Safe Browsing", "safe": False,
                        "details": "URL matched threat signatures", "matches": data["matches"]}
            return {"source": "Google Safe Browsing", "safe": True, "details": "No threats found"}
    except Exception:
        pass
    return {"source": "Google Safe Browsing", "safe": True, "details": "Error querying API"}

def check_sql_injection(url: str) -> dict:
    """Check for basic SQL injection patterns in the decoded URL."""
    decoded_url = urllib.parse.unquote(url)
    sql_patterns = [
        r"(?i)\bUNION\b\s+(?:ALL\s+)?\bSELECT\b",
        r"(?i)\bSELECT\b\s+.*?[\w\*]\s+\bFROM\b",
        r"(?i)\bINSERT\b\s+\bINTO\b",
        r"(?i)\bUPDATE\b\s+\w+\s+\bSET\b",
        r"(?i)\bDROP\b\s+(?:TABLE|DATABASE|INDEX)\b",
        r"(?i)\bOR\b\s+\d+\s*=\s*\d+",
        r"(?i)\bOR\b\s+'.*?'\s*=\s*'.*?'",
        r"(?i)\bAND\b\s+\d+\s*=\s*\d+",
        r"(?i)--\s*$",
        r"(?i)\bEXEC\b\s*\("
    ]
    matches = []
    for pattern in sql_patterns:
        found = re.findall(pattern, decoded_url)
        if found:
            matches.extend(found)
    
    if matches:
        return {"detected": True, "details": "SQL Injection patterns found in URL", "matches": list(set([str(m) for m in matches]))}
    return {"detected": False, "details": "No SQL Injection signatures detected", "matches": []}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": os.path.exists(MODEL_PATH)}


@app.post("/register")
def register(
    user: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user with optional email verification."""
    # Check rate limit
    check_rate_limit(request, "register")
    
    # Check if username exists
    if db.query(DBUser).filter(DBUser.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists (only if email column exists)
    try:
        if user.email and db.query(DBUser).filter(DBUser.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
    except Exception:
        # Email column might not exist in old database
        pass
    
    # Create verification token if email provided
    verification_token = None
    if user.email:
        try:
            verification_token = create_verification_token(user.email)
        except Exception:
            verification_token = None
    
    # Create new user - handle both old and new database schemas
    try:
        # Try with new schema (has email fields)
        new_user = DBUser(
            username=user.username,
            password_hash=get_password_hash(user.password),
            email=user.email,
            is_verified=0 if user.email else 1,
            verification_token=verification_token
        )
    except Exception:
        # Fallback to old schema (no email fields)
        new_user = DBUser(
            username=user.username,
            password_hash=get_password_hash(user.password)
        )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send verification email if email provided and token created
    if user.email and verification_token:
        try:
            email_service.send_verification_email(user.email, user.username, verification_token)
            return {
                "message": "Registration successful! Please check your email to verify your account.",
                "user_id": new_user.id,
                "email_sent": True
            }
        except Exception:
            # Email sending failed, but registration succeeded
            return {
                "message": "Registration successful! Email verification configured but not sending (check SMTP settings).",
                "user_id": new_user.id,
                "email_sent": False
            }
    
    return {
        "message": "Registration successful!",
        "user_id": new_user.id,
        "email_sent": False
    }


@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Login with rate limiting."""
    # Check rate limit
    check_rate_limit(request, "login")
    
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Note: Email verification is optional - users can login even without verified email
    # This allows backward compatibility with old database and users who registered without email
    
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}


@app.get("/history")
def get_history(
    current_user: Optional[DBUser] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    rows = (
        db.query(ScanHistory)
        .filter(ScanHistory.user_id == current_user.id)
        .order_by(ScanHistory.timestamp.desc())
        .all()
    )
    return [
        {
            "id": r.id, "url": r.url, "prediction": r.prediction,
            "confidence_score": r.confidence_score, "risk_score": r.risk_score,
            "timestamp": str(r.timestamp)
        }
        for r in rows
    ]


@app.post("/predict")
def predict(
    req: URLRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_optional_user)
):
    """Predict if URL is phishing with hybrid detection (ML + Rules)."""
    # Check rate limit
    check_rate_limit(request, "scan")
    
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=422, detail="URL must not be empty")

    # ── Layer 1: Advanced Rule-Based Detection ─────────────────────────────
    advanced_result = advanced_url_analysis(url)
    
    # Only override ML if there are STRONG indicators (multiple HIGH severity)
    # This prevents false positives on legitimate URLs
    should_override = (
        advanced_result['should_block'] or  # Explicit block flag
        (advanced_result['risk_score'] >= 80 and advanced_result['total_indicators'] >= 2) or  # High risk + multiple indicators
        advanced_result['typosquatting']['detected']  # Typosquatting is always suspicious
    )
    
    if should_override:
        # Force phishing prediction
        prediction = "Phishing"
        is_phishing = True
        risk_score = max(advanced_result['risk_score'], 80)  # Minimum 80% risk
        confidence = 90.0 + (risk_score - 80) * 0.99  # Scale to 90-99.9%
        confidence = min(confidence, 99.9)
        
        # Still run ML for comparison
        model, meta = _load_model()
        ext = tldextract.extract(url)
        root_domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
        feat_dict = extract_features(url)
        X_row = np.array([[feat_dict[k] for k in FEATURE_NAMES]])
        proba = model.predict_proba(X_row)[0]
        ml_phish_prob = float(proba[1])
    else:
        # ── Layer 2: ML Model Prediction ───────────────────────────────────
        model, meta = _load_model()

        # Extract Domain
        ext = tldextract.extract(url)
        root_domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain

        # Feature extraction
        feat_dict = extract_features(url)
        X_row = np.array([[feat_dict[k] for k in FEATURE_NAMES]])

        # Inference
        proba = model.predict_proba(X_row)[0]
        phish_prob = float(proba[1])
        is_phishing = phish_prob >= 0.5
        prediction = "Phishing" if is_phishing else "Legitimate"
        confidence = round(max(proba) * 100, 2)
        risk_score = round(phish_prob * 100, 2)
        ml_phish_prob = phish_prob

    # Risk level
    if risk_score < 30:
        risk_level = "Safe"
    elif risk_score < 70:
        risk_level = "Suspicious"
    else:
        risk_level = "Dangerous"

    # SHAP explanation
    shap_list = get_shap_explanation(model, X_row, FEATURE_NAMES)
    top_suspicious = [s for s in shap_list[:15] if s["shap_value"] > 0][:8]

    # Threat intel & OSINT
    threat_intel = check_safe_browsing(url)
    domain_age_days = get_domain_age(root_domain)
    
    # SQL Injection detection
    sql_injection_intel = check_sql_injection(url)

    # Save to DB
    if current_user:
        db.add(ScanHistory(
            user_id=current_user.id, url=url, prediction=prediction,
            confidence_score=confidence, risk_score=risk_score
        ))
        db.commit()

    return {
        "url":                     url,
        "prediction":              prediction,
        "is_phishing":             is_phishing,
        "confidence_score":        confidence,
        "risk_score":              risk_score,
        "risk_level":              risk_level,
        "domain_age_days":         domain_age_days,
        "features":                feat_dict,
        "top_suspicious":          top_suspicious,
        "all_shap":                shap_list[:20],
        "threat_intel":            threat_intel,
        "sql_injection":           sql_injection_intel,
        # Advanced detection results
        "advanced_detection": {
            "enabled": True,
            "should_block": advanced_result['should_block'],
            "typosquatting_detected": advanced_result['typosquatting']['detected'],
            "suspicious_patterns": advanced_result['suspicious_patterns']['detected'],
            "total_indicators": advanced_result['total_indicators'],
            "findings": advanced_result['findings'][:5],  # Top 5 findings
            "ml_vs_rules": {
                "ml_prediction": "Phishing" if ml_phish_prob >= 0.5 else "Legitimate",
                "ml_risk_score": round(ml_phish_prob * 100, 2),
                "rules_overrode_ml": advanced_result['should_block'] and ml_phish_prob < 0.5
            }
        }
    }


@app.get("/model-info")
def model_info():
    _, meta = _load_model()
    if meta is None:
        raise HTTPException(status_code=404, detail="Run train.py first")
    return meta


# ── Email Verification & Security Endpoints ───────────────────────────────────

@app.post("/verify-email")
def verify_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify user email with token."""
    # Decode verification token
    payload = decode_verification_token(request.token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token payload")
    
    # Find user by email
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already verified
    if user.is_verified:
        return {"message": "Email already verified", "verified": True}
    
    # Verify the user
    user.is_verified = 1
    user.verification_token = None
    db.commit()
    
    # Send welcome email
    email_service.send_welcome_email(user.email, user.username)
    
    return {"message": "Email verified successfully! You can now login.", "verified": True}


@app.post("/resend-verification")
def resend_verification(
    email_data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Resend verification email."""
    check_rate_limit(request, "register")  # Use same rate limit as registration
    
    user = db.query(DBUser).filter(DBUser.email == email_data.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a verification link has been sent"}
    
    if user.is_verified:
        return {"message": "Email is already verified"}
    
    # Create new verification token
    verification_token = create_verification_token(user.email)
    user.verification_token = verification_token
    db.commit()
    
    # Send verification email
    email_service.send_verification_email(user.email, user.username, verification_token)
    
    return {"message": "Verification email sent successfully"}


@app.post("/forgot-password")
def forgot_password(
    request_data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset email."""
    check_rate_limit(request, "login")
    
    user = db.query(DBUser).filter(DBUser.email == request_data.email).first()
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Create password reset token (reuse verification token logic)
    reset_token = create_verification_token(user.email)  # Could create separate function
    user.verification_token = reset_token
    db.commit()
    
    # Send password reset email
    email_service.send_password_reset_email(user.email, user.username, reset_token)
    
    return {"message": "Password reset email sent successfully"}


@app.post("/reset-password")
def reset_password(
    request_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with token."""
    # Decode token
    payload = decode_verification_token(request_data.token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    email = payload.get("sub")
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password_hash = get_password_hash(request_data.new_password)
    user.verification_token = None
    db.commit()
    
    return {"message": "Password reset successfully! You can now login with your new password."}


@app.get("/user/profile")
def get_user_profile(
    current_user: DBUser = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_verified": bool(current_user.is_verified),
        "created_at": str(current_user.created_at) if hasattr(current_user, 'created_at') else None
    }


@app.post("/user/delete-account")
def delete_account(
    request: Request,
    current_user: DBUser = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Delete all scan history for this user
    db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id).delete()
    
    # Delete user
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully. All your data has been removed."}


# ── Static frontend ───────────────────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def root():
    idx = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx)
    return {"message": "PhishGuard API running. Frontend not found."}
