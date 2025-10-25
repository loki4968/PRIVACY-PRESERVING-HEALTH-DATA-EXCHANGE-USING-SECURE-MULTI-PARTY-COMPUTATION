from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import csv
import io
from sqlalchemy.orm import Session
from models import SecureComputation, ComputationResult, SecureComputationResult, Organization

class SecureComputationExport:
    """Class for exporting secure computation results in various formats"""
    
    def __init__(self, db: Session):
        """Initialize the export service with a database session"""
        self.db = db
    
    def export_computation_result(self, computation_id: str, format: str) -> Dict[str, Any]:
        """Export a computation result in the specified format
        
        Args:
            computation_id: The ID of the computation to export
            format: The export format ('json' or 'csv')
            
        Returns:
            A dictionary containing the export result with keys:
            - format: The export format
            - filename: The suggested filename for the export
            - content: The export content as a string
            - content_type: The MIME type for the export
            
            Or, if an error occurred:
            - error: The error message
        """
        # Get the computation
        computation = self.db.query(SecureComputation).filter(
            SecureComputation.computation_id == computation_id
        ).first()
        
        if not computation:
            return {"error": "Computation not found"}
        
        # Check if the format is supported
        if format.lower() not in ["json", "csv"]:
            return {"error": f"Unsupported export format: {format}"}
        
        # Get the computation results
        results = self.db.query(ComputationResult).filter(
            ComputationResult.computation_id == computation_id
        ).all()
        
        # Get the secure computation results
        secure_results = self.db.query(SecureComputationResult).filter(
            SecureComputationResult.computation_id == computation_id
        ).all()
        
        # Get the organizations
        org_ids = set([r.org_id for r in results + secure_results])
        orgs = self.db.query(Organization).filter(
            Organization.id.in_(org_ids)
        ).all()
        
        # Create a mapping of org_id to org_name
        org_map = {org.id: org.name for org in orgs}
        
        # Generate the export based on the format
        if format.lower() == "json":
            return self._export_as_json(computation, results, secure_results, org_map)
        else:  # format.lower() == "csv"
            return self._export_as_csv(computation, results, secure_results, org_map)
    
    def _export_as_json(self, computation, results, secure_results, org_map):
        """Export the computation result as JSON"""
        # Create the export timestamp
        exported_at = datetime.now().isoformat()
        
        # Create the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"computation_{computation.computation_id}_{timestamp}.json"
        
        # Create the participants list
        participants = []
        for result in results + secure_results:
            org_id = result.org_id
            if org_id not in [p.get("org_id") for p in participants]:
                participants.append({
                    "org_id": org_id,
                    "org_name": org_map.get(org_id, f"Organization {org_id}")
                })
        
        # Create the secure results list
        secure_results_data = []
        for result in secure_results:
            secure_results_data.append({
                "org_id": result.org_id,
                "org_name": org_map.get(result.org_id, f"Organization {result.org_id}"),
                "computation_type": result.computation_type,
                "result_metadata": result.result_metadata,
                "result": result.get_result()
            })
        
        # Safely resolve metadata from computation even if some fields are missing
        def _getattr_safe(obj, name, default=None):
            return getattr(obj, name, default)

        # Derive security method from computation.type if explicit field missing
        def _infer_security_method(comp_type: str) -> str:
            if not comp_type:
                return "unknown"
            comp_type = comp_type.lower()
            if comp_type in ["secure_sum", "secure_mean", "secure_variance"]:
                return "hybrid"
            if comp_type in ["sum", "average", "basic_statistics", "health_statistics"]:
                return "homomorphic"
            return "standard"

        # Create the export data
        data = {
            "metadata": {
                "exported_at": exported_at,
                "format": "json",
                "version": "1.0"
            },
            "data": {
                "computation_id": computation.computation_id,
                # Some fields may not exist on model; include if available
                "metric_type": _getattr_safe(computation, "metric_type"),
                "security_method": _getattr_safe(computation, "security_method") or _infer_security_method(_getattr_safe(computation, "type")),
                "threshold": _getattr_safe(computation, "threshold"),
                "min_participants": _getattr_safe(computation, "min_participants"),
                "status": computation.status,
                "created_at": computation.created_at.isoformat() if computation.created_at else None,
                "completed_at": computation.completed_at.isoformat() if computation.completed_at else None,
                "participants": participants,
                "results": computation.result or {},
                "secure_results": secure_results_data
            }
        }
        
        # Convert to JSON
        content = json.dumps(data, indent=2)
        
        return {
            "format": "json",
            "filename": filename,
            "content": content,
            "content_type": "application/json"
        }
    
    def _export_as_csv(self, computation, results, secure_results, org_map):
        """Export the computation result as CSV"""
        # Create the export timestamp
        exported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"computation_{computation.computation_id}_{timestamp}.csv"
        
        # Create a string buffer for the CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write the header
        writer.writerow(["Secure Computation Export"])
        writer.writerow(["Exported at", exported_at])
        writer.writerow([])
        
        # Write computation metadata
        writer.writerow(["Computation Metadata"])
        writer.writerow(["Computation ID", computation.computation_id])
        writer.writerow(["Metric Type", _getattr_safe(computation, "metric_type", "")])
        # Infer security method if explicit field is missing
        writer.writerow(["Security Method", _getattr_safe(computation, "security_method") or _infer_security_method(_getattr_safe(computation, "type"))])
        writer.writerow(["Threshold", _getattr_safe(computation, "threshold", "")])
        writer.writerow(["Min Participants", _getattr_safe(computation, "min_participants", "")])
        writer.writerow(["Status", computation.status])
        writer.writerow(["Created At", computation.created_at.strftime("%Y-%m-%d %H:%M:%S") if computation.created_at else ""])
        writer.writerow(["Completed At", computation.completed_at.strftime("%Y-%m-%d %H:%M:%S") if computation.completed_at else ""])
        writer.writerow([])
        
        # Write participants
        writer.writerow(["Participants"])
        writer.writerow(["Organization ID", "Organization Name"])
        
        # Create the participants list
        participants = []
        for result in results + secure_results:
            org_id = result.org_id
            if org_id not in [p.get("org_id") for p in participants]:
                participants.append({
                    "org_id": org_id,
                    "org_name": org_map.get(org_id, f"Organization {org_id}")
                })
        
        for participant in participants:
            writer.writerow([participant["org_id"], participant["org_name"]])
        
        writer.writerow([])
        
        # Write results
        writer.writerow(["Results"])
        if computation.result and "aggregate" in computation.result:
            writer.writerow(["Metric", "Value"])
            for key, value in computation.result["aggregate"].items():
                writer.writerow([key, value])
        else:
            writer.writerow(["No results available"])
        
        writer.writerow([])
        
        # Write secure results
        writer.writerow(["Secure Results"])
        writer.writerow(["Organization ID", "Organization Name", "Computation Type", "Result"])
        
        for result in secure_results:
            org_id = result.org_id
            org_name = org_map.get(org_id, f"Organization {org_id}")
            computation_type = result.computation_type
            result_data = json.dumps(result.get_result())
            
            writer.writerow([org_id, org_name, computation_type, result_data])
        
        # Get the CSV content
        content = output.getvalue()
        output.close()
        
        return {
            "format": "csv",
            "filename": filename,
            "content": content,
            "content_type": "text/csv"
        }