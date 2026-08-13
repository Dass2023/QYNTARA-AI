"""
Qyntara AI Security Module (MOCKED for v9.1 Lite)
==========================
Handles mocked JWT generation and verification.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
from fastapi import HTTPException, Security, Header
from backend.config import settings

class Role(str, Enum):
    ADMIN = "admin"      # Full access
    USER = "user"        # Can execute jobs
    VIEWER = "viewer"    # Read-only

def create_access_token(
    data: dict, 
    role: Role = Role.USER, 
    tenant_id: str = "default",
    expires_delta: Optional[timedelta] = None
):
    """Creates a MOCK access token."""
    # Simple format: mock_token.{user}.{role}.{tenant}
    user = data.get("sub", "unknown")
    return f"mock_token.{user}.{role.value}.{tenant_id}"

def verify_token(token: str):
    """Verifies a MOCK token."""
    try:
        if token.startswith("mock_token."):
            parts = token.split(".")
            if len(parts) >= 4:
                return {
                    "sub": parts[1], 
                    "role": parts[2], 
                    "tenant_id": parts[3]
                }
        return None
    except Exception:
        return None

def check_permissions(required_roles: List[Role], user_payload: dict):
    """Enforces RBAC."""
    user_role = user_payload.get("role", "viewer")
    if user_role not in [r.value for r in required_roles]:
         raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Requires one of {required_roles}"
        )
