from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from enum import Enum

SECRET_KEY = os.getenv("SECRET_KEY", "qyntara-dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Define Role Enum locally to avoid circular dependency if models.py is also missing
class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, role: Role, tenant_id: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "role": role.value, "tenant_id": tenant_id})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def check_permissions(required_roles: List[Role], user: dict):
    # If using API Key bypass, role is injected as string, handle that
    user_role = user.get("role")
    
    # Allow if role matches
    if user_role in [r.value for r in required_roles]:
        return True
        
    return False
