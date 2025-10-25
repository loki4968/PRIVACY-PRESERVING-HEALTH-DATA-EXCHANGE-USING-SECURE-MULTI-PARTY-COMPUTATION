from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import uuid
import json
import random


class SecureComputationMock:
    """Mock implementation of the secure computation service for testing and development"""
    
    def __init__(self):
        self.computations = {}
        
    def create_computation(self, org_id: int, computation_type: str) -> str:
        """Create a new secure computation"""
        computation_id = str(uuid.uuid4())
        
        self.computations[computation_id] = {
            "computation_id": computation_id,
            "org_id": org_id,
            "type": computation_type,
            "status": "initialized",
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "completed_at": None,
            "participants": [],
            "submissions": [],
            "result": None,
            "error_message": None,
            "error_code": None
        }
        
        return computation_id
    
    def join_computation(self, computation_id: str, org_id: int) -> bool:
        """Join an existing computation"""
        if computation_id not in self.computations:
            return False
            
        if org_id not in self.computations[computation_id]["participants"]:
            self.computations[computation_id]["participants"].append(org_id)
            
        return True
    
    def submit_data(self, computation_id: str, org_id: int, data_points: List[float]) -> Dict[str, Any]:
        """Submit data for a computation"""
        if computation_id not in self.computations:
            return {
                "success": False,
                "error": "Computation not found",
                "error_code": "COMPUTATION_NOT_FOUND"
            }
            
        # Add submission
        self.computations[computation_id]["submissions"].append({
            "org_id": org_id,
            "data_points": data_points,
            "submitted_at": datetime.utcnow()
        })
        
        # Update computation status
        if self.computations[computation_id]["status"] == "initialized":
            self.computations[computation_id]["status"] = "waiting_for_data"
            self.computations[computation_id]["updated_at"] = datetime.utcnow()
            
        return {
            "success": True,
            "message": "Data submitted successfully",
            "data_points_count": len(data_points)
        }
    
    def perform_computation(self, computation_id: str) -> bool:
        """Perform the secure computation"""
        if computation_id not in self.computations:
            return False
            
        computation = self.computations[computation_id]
        
        # Check if already completed
        if computation["status"] == "completed":
            return True
            
        # Check if there are submissions
        if not computation["submissions"]:
            computation["status"] = "error"
            computation["error_message"] = "No data submitted for computation"
            computation["error_code"] = "NO_DATA_SUBMITTED"
            computation["updated_at"] = datetime.utcnow()
            return False
            
        # Generate mock result based on computation type
        try:
            # Extract all data points
            all_data = []
            for submission in computation["submissions"]:
                all_data.extend(submission["data_points"])
                
            # Calculate basic statistics
            result = {
                "count": len(all_data),
                "organizations_count": len(set(s["org_id"] for s in computation["submissions"])),
                "computation_type": computation["type"],
                "timestamp": datetime.utcnow().isoformat(),
                "secure_computation_method": "mock",
                "final_result": sum(all_data) / len(all_data) if all_data else 0,
                "num_parties": len(computation["participants"])
            }
            
            # Update computation with results
            computation["result"] = result
            computation["status"] = "completed"
            computation["completed_at"] = datetime.utcnow()
            computation["updated_at"] = datetime.utcnow()
            return True
        except Exception as e:
            computation["status"] = "error"
            computation["error_message"] = f"Error calculating statistics: {str(e)}"
            computation["error_code"] = "CALCULATION_ERROR"
            computation["updated_at"] = datetime.utcnow()
            return False