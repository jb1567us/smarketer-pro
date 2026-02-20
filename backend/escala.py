import json
import time
import logging
from typing import Dict, Any, Optional
from backend.database import get_connection

logger = logging.getLogger(__name__)

class EscalaProtocol:
    """
    Singleton for managing high-risk operation guardrails.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EscalaProtocol, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        logger.info("🛡️ Escala Protocol Initialized.")

    def check_risk(self, operation_type: str, context: Dict[str, Any]) -> bool:
        """
        Evaluates risk thresholds. Returns True if safe, 
        or triggers escalation and returns False if blocked.
        """
        # Define Risk Thresholds
        is_high_risk = False
        risk_reason = ""

        # 1. Proxy Cost Threshold
        if context.get("proxy_cost", 0) > 5.0:
            is_high_risk = True
            risk_reason = f"High proxy spend detected: ${context.get('proxy_cost')}"

        # 2. Destructive Operations
        elif operation_type in ["bulk_delete", "database_wipe"]:
            is_high_risk = True
            risk_reason = f"Critical operation attempted: {operation_type}"

        # 3. Mass Export
        elif operation_type == "full_export" and context.get("profile_count", 0) > 100:
            is_high_risk = True
            risk_reason = f"Mass profile export detected: {context.get('profile_count')} profiles"

        if is_high_risk:
            logger.warning(f"⚠️ [Escala] Risk Blocked: {risk_reason}")
            self.request_escalation(operation_type, context, risk_reason)
            return False

        return True

    def request_escalation(self, op_type: str, context: Dict[str, Any], reason: str):
        """
        Registers a pending escalation request in the database.
        """
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO escalations (operation_type, risk_level, context_json, status, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (op_type, "critical", json.dumps({"reason": reason, "context": context}), "pending", int(time.time())))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"[Escala] DB Error: {e}")

# Global singleton
escala = EscalaProtocol()
