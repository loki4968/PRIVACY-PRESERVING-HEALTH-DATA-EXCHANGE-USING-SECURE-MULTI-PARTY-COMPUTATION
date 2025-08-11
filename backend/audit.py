from fastapi import Request
from sqlalchemy.orm import Session
from database import AuditLog, Organization
from datetime import datetime
import json
from typing import Optional, Any, Dict

class AuditLogger:
    def __init__(self, db: Session):
        self.db = db

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
            print(f"Failed to create audit log: {str(e)}")

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