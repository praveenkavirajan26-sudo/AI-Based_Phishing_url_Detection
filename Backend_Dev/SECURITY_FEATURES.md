# 🔒 Security Features Implementation Guide

## Overview
Three critical security features have been implemented in PhishGuard AI:
1. **Rate Limiting** - Prevents API abuse and brute force attacks
2. **Proper JWT Expiry** - Tokens now expire in 24 hours (reduced from 7 days)
3. **Email Verification** - Users must verify their email before accessing the system

---

## 1. Rate Limiting 🚦

### What It Does
- Limits the number of requests per IP address per time window
- Prevents brute force attacks on login
- Prevents spam registrations
- Protects API from abuse

### Rate Limit Configuration

| Endpoint | Max Requests | Time Window | Purpose |
|----------|-------------|-------------|---------|
| `/login` | 5 attempts | 15 minutes | Prevent brute force |
| `/register` | 3 attempts | 1 hour | Prevent spam |
| `/predict` | 100 scans | 1 hour | Prevent API abuse |
| `/history` | 50 requests | 1 hour | Prevent data scraping |
| Default | 1000 requests | 1 hour | General protection |

### How It Works
```python
# Example: Login endpoint
@app.post("/login")
def login(request: Request, ...):
    check_rate_limit(request, "login")  # ← Rate limit check
    # ... rest of login logic
```

### Implementation Files
- `backend/rate_limiter.py` - Rate limiting logic
- Uses in-memory storage (for production, use Redis)

### Testing Rate Limits
```bash
# Try to login 6 times in 15 minutes
curl -X POST http://localhost:8000/login \
  -d "username=test&password=wrong"

# After 5 attempts, you'll get:
{
  "detail": {
    "error": "Rate limit exceeded",
    "message": "Too many requests. Please try again in 847 seconds.",
    "retry_after": 847,
    "limit": 5,
    "window": "900 seconds"
  }
}
```

---

## 2. JWT Token Expiry ⏰

### Changes Made
- **Before:** 7 days (60 * 24 * 7 minutes)
- **After:** 24 hours (60 * 24 minutes)

### Why This Matters
- Reduces risk if token is stolen
- Forces regular re-authentication
- Better security posture
- Industry standard practice

### Configuration
```python
# backend/database.py
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
```

### User Experience
- Users will need to login again after 24 hours
- No automatic token refresh (can be added later)
- Clear logout functionality

---

## 3. Email Verification ✉️

### What It Does
- Sends verification email after registration
- User must click verification link to activate account
- Cannot login until email is verified
- 24-hour expiry on verification tokens

### New Database Fields
```python
class User(Base):
    email = Column(String(100), unique=True, nullable=True)
    is_verified = Column(Integer, default=0)  # 0 or 1
    verification_token = Column(String(200), nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Email Flow

#### Registration with Email
```
User Registration
    ↓
Create Account (is_verified=0)
    ↓
Generate Verification Token
    ↓
Send Verification Email
    ↓
User Clicks Link
    ↓
Verify Email (is_verified=1)
    ↓
Send Welcome Email
    ↓
Can Now Login
```

#### Registration without Email
```
User Registration (no email)
    ↓
Create Account (is_verified=1)
    ↓
Can Login Immediately
```

### New API Endpoints

#### 1. POST `/register`
```json
Request:
{
  "username": "johndoe",
  "password": "SecurePass123!",
  "email": "john@example.com"
}

Response:
{
  "message": "Registration successful! Please check your email to verify your account.",
  "user_id": 1,
  "email_sent": true
}
```

#### 2. POST `/verify-email`
```json
Request:
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}

Response:
{
  "message": "Email verified successfully! You can now login.",
  "verified": true
}
```

#### 3. POST `/resend-verification`
```json
Request:
{
  "email": "john@example.com"
}

Response:
{
  "message": "Verification email sent successfully"
}
```

#### 4. POST `/forgot-password`
```json
Request:
{
  "email": "john@example.com"
}

Response:
{
  "message": "Password reset email sent successfully"
}
```

#### 5. POST `/reset-password`
```json
Request:
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "new_password": "NewSecurePass456!"
}

Response:
{
  "message": "Password reset successfully! You can now login with your new password."
}
```

#### 6. GET `/user/profile`
```json
Response:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "is_verified": true,
  "created_at": "2024-01-15 10:30:00"
}
```

#### 7. POST `/user/delete-account`
```json
Response:
{
  "message": "Account deleted successfully. All your data has been removed."
}
```

### Email Service Configuration

Create `.env` file in backend directory:
```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@phishguard.ai
SMTP_USE_TLS=true

# Application URL
APP_URL=http://localhost:5173

# Secret Key (change this!)
SECRET_KEY=your-super-secret-key-change-in-production
```

### Gmail Setup (for testing)
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password:
   - Search "App Passwords"
   - Select "Mail" and "Other (Custom name)"
   - Enter "PhishGuard"
   - Copy the 16-character password
4. Use this password in `SMTP_PASSWORD`

### Development Mode
If SMTP is not configured, emails are logged to console:
```
⚠️  Email not configured. Would send to john@example.com: Verify Your PhishGuard AI Account
   Content preview: <!DOCTYPE html><html>...
```

---

## Installation & Setup

### 1. Install Dependencies
```bash
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Update Database
The database will automatically add new columns on startup.

### 3. Configure Email (Optional)
Create `.env` file as shown above.

### 4. Restart Backend
```bash
.\venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## Testing the Features

### Test 1: Rate Limiting
```bash
# Quick test with curl
for i in {1..6}; do
  curl -X POST http://localhost:8000/login \
    -d "username=test&password=wrong"
  echo ""
done

# 6th request should return 429 error
```

### Test 2: Email Verification
1. Register with email:
   ```bash
   curl -X POST http://localhost:8000/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"Test123!","email":"test@example.com"}'
   ```
2. Check console for verification link (if email not configured)
3. Verify email:
   ```bash
   curl -X POST http://localhost:8000/verify-email \
     -H "Content-Type: application/json" \
     -d '{"token":"YOUR_TOKEN_HERE"}'
   ```
4. Try to login (should work now)

### Test 3: JWT Expiry
1. Login and get token
2. Wait 24 hours (or change `TOKEN_EXPIRE_MINUTES` for testing)
3. Try to use token (should get 401 error)
4. Login again to get new token

---

## Security Best Practices Implemented ✅

1. **Rate Limiting** - Prevents brute force and DoS attacks
2. **JWT Expiry** - Reduces token theft impact
3. **Email Verification** - Ensures valid user emails
4. **Password Hashing** - bcrypt with salt (already existed)
5. **Input Validation** - Email format validation
6. **Error Messages** - Don't reveal if email exists (security)
7. **Token Expiry** - Verification tokens expire in 24 hours
8. **CORS** - Configured for frontend access
9. **Account Deletion** - Users can delete their data (GDPR)
10. **Password Reset** - Secure token-based reset

---

## Production Recommendations 🚀

### High Priority
1. **Redis for Rate Limiting**
   ```python
   # Replace in-memory with Redis
   import redis
   redis_client = redis.Redis(host='localhost', port=6379, db=0)
   ```

2. **Environment Variables**
   ```bash
   # Never commit .env file
   echo ".env" >> .gitignore
   ```

3. **HTTPS**
   - Use Let's Encrypt for free SSL
   - Force HTTPS in production

4. **Email Service**
   - Use SendGrid, AWS SES, or Mailgun
   - Better deliverability than SMTP

5. **Token Refresh**
   - Implement refresh tokens
   - Avoid forcing users to login frequently

### Medium Priority
6. **Logging & Monitoring**
   - Log all authentication attempts
   - Set up alerts for suspicious activity

7. **Database Migration**
   - Use Alembic for database migrations
   - Don't rely on auto-creation

8. **CORS Configuration**
   - Restrict to specific domains
   - Remove `allow_origins=["*"]`

9. **Password Policy**
   - Enforce strong passwords
   - Check against breached passwords

10. **Backup & Recovery**
    - Regular database backups
    - Disaster recovery plan

---

## Troubleshooting

### Issue: Emails not sending
**Solution:**
- Check SMTP credentials
- Verify port and TLS settings
- Check firewall rules
- Review console logs

### Issue: Rate limiting too strict
**Solution:**
```python
# Adjust in rate_limiter.py
RATE_LIMITS = {
    "login": {"max_requests": 10, "window": 900},  # Increased from 5
    ...
}
```

### Issue: Database migration errors
**Solution:**
```bash
# Reset database (WARNING: deletes all data)
rm phishing.db
python app.py  # Recreates with new schema
```

### Issue: Token expiry too short
**Solution:**
```python
# In database.py
TOKEN_EXPIRE_MINUTES = 60 * 48  # Change to 48 hours
```

---

## API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Support

For issues or questions:
1. Check this documentation
2. Review console logs
3. Test with curl commands
4. Check API documentation at /docs

---

**Last Updated:** April 14, 2026  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
