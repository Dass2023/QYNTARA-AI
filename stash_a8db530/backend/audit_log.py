"""
Qyntara AI - Enterprise Audit Logging Service
Immutable JSON-line logs for SOC2/TISAX compliance.
"""

import json
import time
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure specific logger for audit
audit_logger = logging.getLogger("qyntara.audit")
audit_logger.setLevel(logging.INFO)

# File handler ensures strictly appended logs
log_dir = "backend/logs"
os.makedirs(log_dir, exist_ok=True)
handler = logging.FileHandler(os.path.join(log_dir, "audit.jsonl"))
handler.setFormatter(logging.Formatter('%(message)s'))
audit_logger.addHandler(handler)

class AuditLog:
    @staticmethod
    def log(
        user_id: str,
        role: str,
        action: str,
        resource: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = "default"
    ):
        """
        Records an immutable audit event.
        Format: timestamp | tenant | user | role | action | resource | status | details
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "timestamp_unix": time.time(),
            "tenant_id": tenant_id,
            "user_id": user_id,
            "role": role,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {}
        }
        
        # Write immutable JSON line
        audit_logger.info(json.dumps(event))

    @staticmethod
    def log_access_denied(user_id: str, role: str, resource: str):
        AuditLog.log(
            user_id=user_id,
            role=role,
            action="ACCESS_DENIED",
            resource=resource,
            status="FAILURE",
            details={"reason": "Insufficient Permissions"}
        )
