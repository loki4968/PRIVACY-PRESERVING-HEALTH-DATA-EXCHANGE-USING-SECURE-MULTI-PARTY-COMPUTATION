from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Union
from backend.models import SecureComputation, ComputationParticipant
from backend.dependencies import get_db, get_current_user, require_permissions
from backend.auth_utils import Permission
from backend.secure_computation import SecureComputationService, SecureHealthMetricsComputation
from pydantic import BaseModel

router = APIRouter()

class ComputationCreate(BaseModel):
    computation_type: str
    participating_orgs: List[str]

class ComputationResponse(BaseModel):
    computation_id: str
    type: str
    status: str
    result: Dict[str, Any] = None
    created_at: str
    completed_at: str = None

class MetricSubmission(BaseModel):
    value: Union[float, List[float]]

@router.post("/computations", response_model=ComputationResponse)
def create_computation(
    computation: ComputationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = SecureComputationService(db)
        computation_id = service.create_computation(
            current_user["id"],
            computation.computation_type
        )
        
        # Initialize secure computation
        metrics_computation = SecureHealthMetricsComputation()
        metrics_computation.initialize_computation(
            computation_id,
            computation.computation_type,
            computation.participating_orgs
        )
        
        return service.get_computation_result(computation_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create computation: {str(e)}"
        )

@router.post("/computations/{computation_id}/join")
def join_computation(
    computation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = SecureComputationService(db)
        success = service.join_computation(computation_id, current_user["id"])
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Computation not found"
            )
        return {"message": "Successfully joined computation"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to join computation: {str(e)}"
        )

@router.post("/computations/{computation_id}/submit")
def submit_data(
    computation_id: str,
    submission: MetricSubmission,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = SecureComputationService(db)
        # Convert single value to list if needed
        data = submission.value if isinstance(submission.value, list) else [submission.value]
        success = service.submit_data(computation_id, current_user["id"], data)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Computation not found"
            )
        return {"message": "Successfully submitted data"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit data: {str(e)}"
        )

@router.get("/computations/{computation_id}/result", response_model=Dict[str, Any])
def get_computation_result(
    computation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = SecureComputationService(db)
        result = service.get_computation_result(computation_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Computation not found or not completed"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get computation result: {str(e)}"
        )

@router.post("/computations/{computation_id}/compute")
def compute_result(
    computation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = SecureComputationService(db)
        success = service.perform_computation(computation_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Computation not found or not ready"
            )
        return {"message": "Successfully computed result"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute result: {str(e)}"
        )

@router.get("/computations", response_model=List[ComputationResponse])
def list_computations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = SecureComputationService(db)
        return service.list_computations(current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list computations: {str(e)}"
        ) 