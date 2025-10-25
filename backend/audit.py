from fastapi import Request
from sqlalchemy.orm import Session
from models import AuditLog, Organization
from datetime import datetime
import json
import logging
import os
from typing import Optional, Any, Dict, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("audit")

# Configure file handler if LOG_DIR is set
LOG_DIR = os.environ.get("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "audit.log"))
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class AuditLogger:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        
    def log_event(self, event_type: str, user_id: Optional[Union[int, str]] = None, details: Optional[Dict[str, Any]] = None):
        """Log an event to the audit log file without requiring a database connection.
        
        This is useful for WebSocket events or other scenarios where a database session may not be available.
        
        Args:
            event_type: The type of event (e.g., websocket_connected, websocket_disconnected)
            user_id: The ID of the user or organization associated with the event
            details: Additional details about the event
        """
        try:
            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": user_id,
                "details": details or {}
            }
            
            # Log to file via the logger
            logger.info(f"AUDIT: {json.dumps(event_data)}")
            
            # If a database connection is available, also log to the database
            if self.db is not None:
                try:
                    self.log_action(
                        user_id=user_id if isinstance(user_id, int) else None,
                        action=event_type,
                        resource_type="system",
                        details=details,
                        request=None
                    )
                except Exception as db_error:
                    logger.error(f"Failed to log event to database: {str(db_error)}")
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}")

    def log_action(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log an action to the audit log."""
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
                created_at=datetime.utcnow()
            )
            self.db.add(audit_entry)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            # Log the error but don't raise it to prevent disrupting the main flow
            logger.error(f"Failed to create audit log: {str(e)}")

    def get_user_actions(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> list:
        """Get audit logs for a specific user with optional filters."""
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
            
        return query.order_by(AuditLog.created_at.desc()).all()

    def get_resource_actions(
        self,
        resource_type: str,
        resource_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list:
        """Get audit logs for a specific resource."""
        query = self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        )
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
            
        return query.order_by(AuditLog.created_at.desc()).all()

    def export_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """Export audit logs in the specified format."""
        query = self.db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
            
        logs = query.order_by(AuditLog.created_at.desc()).all()
        
        if format == "json":
            return json.dumps([{
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "created_at": log.created_at.isoformat()
            } for log in logs], indent=2)
        elif format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "ID", "User ID", "Action", "Resource Type", "Resource ID",
                "Details", "IP Address", "User Agent", "Created At"
            ])
            
            for log in logs:
                writer.writerow([
                    log.id,
                    log.user_id,
                    log.action,
                    log.resource_type,
                    log.resource_id,
                    json.dumps(log.details),
                    log.ip_address,
                    log.user_agent,
                    log.created_at.isoformat()
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Example usage:
# audit_logger = AuditLogger(db)
# audit_logger.log_action(
#     user_id=1,
#     action="login",
#     resource_type="user",
#     resource_id=1,
#     details={"status": "success"},
#     request=request
# )