from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import statistics
from typing import List, Dict, Any
from backend.models import Upload, Organization
from backend.dependencies import get_current_user, get_db
import json

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