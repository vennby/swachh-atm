import time
from typing import Optional
import jwt
import hashlib
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET = "CHANGE_THIS_SECRET"  # replace with env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days

# bcrypt via passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def _sha256_hex(s: str) -> str:
    """Return hex digest of SHA-256 for the input string.
    This keeps the bcrypt input short and deterministic to avoid bcrypt's 72-byte limit.
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    """Pre-hash with SHA-256, then hash with bcrypt via passlib."""
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    if len(password) < 6:
        # enforce a small minimum; adjust as you like
        raise ValueError("Password must be at least 6 characters")
    pre = _sha256_hex(password)
    return pwd_context.hash(pre)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against the stored bcrypt hash.
    Pre-hash the plain text with SHA-256 first (same as used during hashing).
    """
    try:
        pre = _sha256_hex(plain)
        return pwd_context.verify(pre, hashed)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    expire = int(time.time()) + (expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload