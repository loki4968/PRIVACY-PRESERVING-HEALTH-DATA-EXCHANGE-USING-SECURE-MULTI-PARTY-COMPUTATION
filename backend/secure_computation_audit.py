from audit import AuditLogger
from typing import Dict, Any, Optional
from fastapi import Request
from sqlalchemy.orm import Session

class SecureComputationAudit:
    """Specialized audit logger for secure computation operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_logger = AuditLogger(db)
    
    def log_computation_initialized(self, user_id: int, computation_id: str, 
                                   metric_type: str, security_method: str,
                                   threshold: Optional[int], min_participants: int,
                                   participating_orgs: list, request: Optional[Request] = None):
        """Log when a secure computation is initialized"""
        details = {
            "computation_id": computation_id,
            "metric_type": metric_type,
            "security_method": security_method,
            "threshold": threshold,
            "min_participants": min_participants,
            "participating_orgs": participating_orgs,
            "action_type": "initialize"
        }
        
        self.audit_logger.log_action(
            user_id=user_id,
            action="secure_computation_initialized",
            resource_type="secure_computation",
            resource_id=computation_id,
            details=details,
            request=request
        )
    
    def log_metric_submitted(self, user_id: int, computation_id: str, 
                           value: float, request: Optional[Request] = None):
        """Log when a metric is submitted to a secure computation"""
        details = {
            "computation_id": computation_id,
            "action_type": "submit",
            # We don't log the actual value for privacy reasons
            "value_submitted": True
        }
        
        self.audit_logger.log_action(
            user_id=user_id,
            action="secure_computation_data_submitted",
            resource_type="secure_computation",
            resource_id=computation_id,
            details=details,
            request=request
        )
    
    def log_computation_executed(self, user_id: int, computation_id: str, 
                               status: str, result_summary: Dict[str, Any] = None,
                               request: Optional[Request] = None):
        """Log when a secure computation is executed"""
        details = {
            "computation_id": computation_id,
            "status": status,
            "action_type": "compute"
        }
        
        # Add a summary of the result without including actual values
        if result_summary:
            # Include metadata about the computation but not the actual values
            if isinstance(result_summary, dict):
                safe_summary = {
                    "computation_completed": True,
                    "participants_count": result_summary.get("organizations_count"),
                    "data_points_count": result_summary.get("data_points_count"),
                    "computation_type": result_summary.get("computation_type"),
                    "secure_computation_method": result_summary.get("secure_computation_method")
                }
                details["result_summary"] = safe_summary
        
        self.audit_logger.log_action(
            user_id=user_id,
            action="secure_computation_executed",
            resource_type="secure_computation",
            resource_id=computation_id,
            details=details,
            request=request
        )
    
    def log_computation_status_checked(self, user_id: int, computation_id: str,
                                     request: Optional[Request] = None):
        """Log when a secure computation's status is checked"""
        details = {
            "computation_id": computation_id,
            "action_type": "status_check"
        }
        
        self.audit_logger.log_action(
            user_id=user_id,
            action="secure_computation_status_checked",
            resource_type="secure_computation",
            resource_id=computation_id,
            details=details,
            request=request
        )
    
    def log_computation_error(self, user_id: int, computation_id: str, 
                            error_code: str, error_message: str,
                            request: Optional[Request] = None):
        """Log when an error occurs in a secure computation"""
        details = {
            "computation_id": computation_id,
            "error_code": error_code,
            "error_message": error_message,
            "action_type": "error"
        }
        
        self.audit_logger.log_action(
            user_id=user_id,
            action="secure_computation_error",
            resource_type="secure_computation",
            resource_id=computation_id,
            details=details,
            request=request
        )