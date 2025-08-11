from typing import List, Dict, Any
from datetime import datetime
import uuid
from backend.models import SecureComputation, ComputationParticipant, ComputationResult
from backend.encryption_utils import EncryptionManager
from backend.smpc_protocols import smpc_protocol
from sqlalchemy.orm import Session
import statistics
import base64
import json
import hashlib
import os

class SecureComputationService:
    def __init__(self, db: Session):
        self.db = db
        self.key = hashlib.sha256(os.urandom(32)).digest()

    def encrypt(self, data: str) -> str:
        return base64.b64encode(hashlib.sha256(data.encode() + self.key).digest()).decode()

    def decrypt(self, data: str) -> str:
        return base64.b64decode(data.encode()).decode()

    def create_computation(self, org_id: int, computation_type: str) -> str:
        computation_id = str(uuid.uuid4())
        computation = SecureComputation(
            computation_id=computation_id,
            org_id=org_id,
            type=computation_type,
            status="initialized"
        )
        self.db.add(computation)
        self.db.commit()
        return computation_id

    def join_computation(self, computation_id: str, org_id: int) -> bool:
        computation = self.db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        if not computation:
            return False
        
        participant = ComputationParticipant(
            computation_id=computation_id,
            org_id=org_id
        )
        self.db.add(participant)
        self.db.commit()
        return True

    def submit_data(self, computation_id: str, org_id: int, data: List[float]) -> bool:
        computation = self.db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        if not computation:
            return False
        
        result = ComputationResult(
            computation_id=computation_id,
            org_id=org_id,
            data_points=data
        )
        self.db.add(result)
        self.db.commit()
        return True

    def get_computation_result(self, computation_id: str) -> Dict[str, Any]:
        computation = self.db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        if not computation:
            return None
        return computation.result

    def perform_computation(self, computation_id: str) -> bool:
        computation = self.db.query(SecureComputation).filter_by(computation_id=computation_id).first()
        if not computation:
            return False
        
        results = self.db.query(ComputationResult).filter_by(computation_id=computation_id).all()
        if not results:
            return False
        
        # Simple aggregation without numpy
        all_data = []
        for result in results:
            all_data.extend(result.data_points)
        
        if not all_data:
            return False
        
        # Calculate basic statistics
        computation.result = {
            "mean": statistics.mean(all_data),
            "median": statistics.median(all_data),
            "std_dev": statistics.stdev(all_data) if len(all_data) > 1 else 0,
            "count": len(all_data),
            "min": min(all_data),
            "max": max(all_data)
        }
        computation.status = "completed"
        computation.completed_at = datetime.utcnow()
        
        self.db.commit()
        return True

    def list_computations(self, org_id: int) -> List[Dict[str, Any]]:
        computations = self.db.query(SecureComputation).filter_by(org_id=org_id).all()
        return [
            {
                "id": c.computation_id,
                "type": c.type,
                "status": c.status,
                "result": c.result,
                "created_at": c.created_at.isoformat(),
                "completed_at": c.completed_at.isoformat() if c.completed_at else None
            }
            for c in computations
        ]

class SecureHealthMetricsComputation:
    def __init__(self):
        self.computations = {}

    def initialize_computation(self, computation_id: str, metric_type: str, participating_orgs: List[str]) -> bool:
        self.computations[computation_id] = {
            "metric_type": metric_type,
            "organizations": set(participating_orgs),
            "shares_submitted": set(),
            "values": {},
            "status": "initialized",
            "start_time": datetime.utcnow().isoformat()
        }
        return True

    def submit_metric(self, computation_id: str, org_id: str, value: float) -> bool:
        if computation_id not in self.computations:
            raise ValueError("Computation not found")
        
        comp = self.computations[computation_id]
        if org_id not in comp["organizations"]:
            raise ValueError("Organization not authorized for this computation")
        
        if org_id in comp["shares_submitted"]:
            raise ValueError("Organization has already submitted a value")
        
        comp["values"][org_id] = value
        comp["shares_submitted"].add(org_id)
        return True

    def compute_aggregate_metrics(self, computation_id: str) -> Dict[str, Any]:
        if computation_id not in self.computations:
            raise ValueError("Computation not found")
        
        comp = self.computations[computation_id]
        if len(comp["shares_submitted"]) < len(comp["organizations"]):
            return None
        
        values = list(comp["values"].values())
        result = {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "count": len(values),
            "min": min(values),
            "max": max(values)
        }
        
        comp["status"] = "completed"
        comp["end_time"] = datetime.utcnow().isoformat()
        comp["result"] = result
        
        return result

    def get_computation_status(self, computation_id: str) -> Dict[str, Any]:
        if computation_id not in self.computations:
            raise ValueError("Computation not found")
        
        comp = self.computations[computation_id]
        return {
            "status": comp["status"],
            "participants_total": len(comp["organizations"]),
            "participants_submitted": len(comp["shares_submitted"]),
            "start_time": comp["start_time"],
            "end_time": comp.get("end_time"),
            "result": comp.get("result")
        }

# Example usage of secure computation
def example_secure_analysis():
    """
    Example of how to use the secure computation service.
    This is just for demonstration purposes.
    """
    # Initialize service
    service = SecureComputationService(db_session)
    
    # Start a new computation
    computation_id = service.create_computation(org_id=1, computation_type="health_statistics")
    
    # Add participants
    service.join_computation(computation_id, org_id=1)
    service.join_computation(computation_id, org_id=2)
    
    # Prepare sample data (in real implementation, this would be encrypted)
    sample_data = [
        {"patient_id": "P1", "value": 120, "type": "blood_pressure"},
        {"patient_id": "P2", "value": 118, "type": "blood_pressure"}
    ]
    
    # Perform secure computation
    result = service.perform_computation(computation_id)
    
    return result 