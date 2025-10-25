from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import statistics
from typing import List, Dict, Any
from models import Upload, Organization
from dependencies import get_current_user, get_db
import json
from services.mental_health_analytics import MentalHealthAnalytics
from services.laboratory_analytics import LaboratoryAnalytics
from services.vital_signs_analytics import VitalSignsAnalytics

router = APIRouter()

def calculate_trend(values: List[float]) -> str:
    if len(values) < 2:
        return "stable"
    return "up" if values[-1] > values[-2] else "down"

def calculate_statistics(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {
            "average": 0,
            "min": 0,
            "max": 0,
            "count": 0,
            "latest": None,
            "trend": "stable",
            "raw_values": []
        }
    
    return {
        "average": statistics.mean(values),
        "min": min(values),
        "max": max(values),
        "count": len(values),
        "latest": values[-1] if values else None,
        "trend": calculate_trend(values),
        "raw_values": values[-10:]  # Last 10 values for trending
    }

@router.get("/metrics")
async def get_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get total uploads
        total_uploads = db.query(Upload).count()
        
        # Get active users in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.query(Organization).filter(
            Organization.last_login >= thirty_days_ago
        ).count()
        
        # Get total analysis count
        total_analysis = db.query(Upload).filter(
            Upload.status == "completed"
        ).count()
        
        # Get recent activity
        recent_uploads = db.query(Upload).filter(
            Upload.org_id == current_user.get("id")
        ).order_by(
            Upload.created_at.desc()
        ).limit(10).all()
        
        recent_activity = []
        for upload in recent_uploads:
            recent_activity.append({
                "type": "upload" if upload.status == "pending" else "analysis",
                "description": f"{upload.filename} - {upload.category}",
                "timestamp": upload.created_at.strftime("%Y-%m-%d %H:%M")
            })
        
        # Get aggregated health metrics
        health_metrics = aggregate_health_metrics(current_user.get("id"), db)
        
        return {
            "total_uploads": total_uploads,
            "active_users": active_users,
            "total_analysis": total_analysis,
            "recent_activity": recent_activity,
            "health_metrics": health_metrics
        }
    except Exception as e:
        print(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch analytics data"
        )

def aggregate_health_metrics(user_id: int, db: Session) -> Dict[str, Any]:
    try:
        print(f"Aggregating health metrics for user {user_id}")
        # Get user's completed uploads
        uploads = db.query(Upload).filter(
            Upload.org_id == user_id,
            Upload.status == "completed"
        ).all()
        print(f"Found {len(uploads)} completed uploads")
        
        # Aggregate metrics from all uploads
        aggregated_data = {
            "blood_sugar": [],
            "blood_pressure": [],
            "heart_rate": []
        }
        
        for upload in uploads:
            print(f"Processing upload {upload.id}")
            try:
                if not upload.result:
                    print(f"Upload {upload.id} has no result")
                    continue
                    
                if isinstance(upload.result, str):
                    result = json.loads(upload.result)
                else:
                    result = upload.result
                
                if not isinstance(result, dict) or "analysis" not in result:
                    print(f"Upload {upload.id} has invalid result format")
                    continue
                    
                analysis = result["analysis"]
                
                # Add metrics to respective arrays
                for metric in ["blood_sugar", "blood_pressure", "heart_rate"]:
                    if metric in analysis and "raw_values" in analysis[metric]:
                        values = analysis[metric]["raw_values"]
                        if isinstance(values, list):
                            aggregated_data[metric].extend(values)
                            print(f"Added {len(values)} values for {metric}")
                
            except Exception as e:
                print(f"Error processing upload {upload.id}: {str(e)}")
                continue
        
        # Calculate statistics for each metric
        metrics_summary = {}
        for metric, values in aggregated_data.items():
            if values:
                try:
                    metrics_summary[metric] = calculate_statistics(values)
                    print(f"Calculated statistics for {metric}: {metrics_summary[metric]}")
                except Exception as e:
                    print(f"Error calculating statistics for {metric}: {str(e)}")
                    continue
        
        if not metrics_summary:
            print("No metrics could be calculated")
            return {
                "blood_sugar": {"count": 0, "raw_values": []},
                "blood_pressure": {"count": 0, "raw_values": []},
                "heart_rate": {"count": 0, "raw_values": []}
            }
            
        return metrics_summary
    except Exception as e:
        print(f"Error in aggregate_health_metrics: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "blood_sugar": {"count": 0, "raw_values": []},
            "blood_pressure": {"count": 0, "raw_values": []},
            "heart_rate": {"count": 0, "raw_values": []}
        }

# ----------------------- Mental Health Analytics ----------------------- #
@router.post("/mental-health/phq9")
async def analyze_phq9(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        responses = payload.get("responses", [])
        service = MentalHealthAnalytics()
        return service.score_phq9(responses)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PHQ-9 analysis failed: {str(e)}")


@router.post("/mental-health/gad7")
async def analyze_gad7(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        responses = payload.get("responses", [])
        service = MentalHealthAnalytics()
        return service.score_gad7(responses)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GAD-7 analysis failed: {str(e)}")


@router.post("/mental-health/suicide-risk")
async def suicide_risk(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        phq9_responses = payload.get("phq9_responses", [])
        risk_flags = payload.get("risk_flags", {})
        service = MentalHealthAnalytics()
        return service.suicide_risk_screen(phq9_responses, risk_flags)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Suicide risk screening failed: {str(e)}")


@router.post("/mental-health/response")
async def treatment_response(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        series = payload.get("series", [])
        service = MentalHealthAnalytics()
        return service.treatment_response(series)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Treatment response analysis failed: {str(e)}")


# ------------------------- Laboratory Analytics ------------------------- #
@router.post("/labs/cbc")
async def analyze_cbc(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        cbc = payload.get("cbc", {})
        service = LaboratoryAnalytics()
        return service.analyze_cbc(cbc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CBC analysis failed: {str(e)}")


@router.post("/labs/cmp")
async def analyze_cmp(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        cmp_panel = payload.get("cmp", {})
        service = LaboratoryAnalytics()
        return service.analyze_cmp(cmp_panel)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CMP analysis failed: {str(e)}")


@router.post("/labs/markers")
async def analyze_infection_markers(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        markers = payload.get("markers", {})
        service = LaboratoryAnalytics()
        return service.analyze_infection_markers(markers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Marker analysis failed: {str(e)}")


@router.post("/labs/summary")
async def labs_summary(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        cbc = payload.get("cbc")
        cmp_panel = payload.get("cmp")
        markers = payload.get("markers")
        service = LaboratoryAnalytics()
        return service.summarize(cbc=cbc, cmp_panel=cmp_panel, markers=markers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lab summary failed: {str(e)}")


# -------------------------- Vital Signs Analytics ----------------------- #
@router.post("/vitals/temperature")
async def vitals_temperature(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        series = payload.get("series", [])
        service = VitalSignsAnalytics()
        return service.analyze_temperature(series)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Temperature analysis failed: {str(e)}")


@router.post("/vitals/sirs")
async def vitals_sirs(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        vitals = payload.get("vitals", {})
        service = VitalSignsAnalytics()
        return service.evaluate_sirs(vitals)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SIRS evaluation failed: {str(e)}")


@router.post("/vitals/bmi")
async def vitals_bmi(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        height_cm = payload.get("height_cm")
        weight_kg = payload.get("weight_kg")
        service = VitalSignsAnalytics()
        return service.bmi(height_cm, weight_kg)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"BMI calculation failed: {str(e)}")


@router.post("/vitals/bmi-trend")
async def vitals_bmi_trend(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        height_cm = payload.get("height_cm")
        weight_series = payload.get("weight_series", [])
        service = VitalSignsAnalytics()
        return service.bmi_trend(height_cm, weight_series)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"BMI trend failed: {str(e)}")


@router.post("/vitals/summary")
async def vitals_summary(
    payload: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
):
    try:
        series = payload.get("series", [])
        service = VitalSignsAnalytics()
        return service.summarize_vitals(series)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Vitals summary failed: {str(e)}")