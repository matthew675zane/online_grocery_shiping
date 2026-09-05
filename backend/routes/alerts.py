from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..services.decision_engine import evaluate_excursion

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.post("", response_model=schemas.AlertDetailResponse)
def create_alert(alert_in: schemas.AlertCreate, db: Session = Depends(get_db)):
    # 1. Create Alert record
    db_alert = models.Alert(
        temperature=alert_in.temperature,
        duration_minutes=alert_in.duration_minutes,
        location=alert_in.location,
        product_class=alert_in.product_class,
        available_actions=alert_in.available_actions,
        status="pending"
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # 2. Run decision engine
    decision = evaluate_excursion(
        alert_in.temperature,
        alert_in.duration_minutes,
        alert_in.location,
        alert_in.product_class,
        alert_in.available_actions
    )
    
    # 3. Create Recommendation record
    db_rec = models.Recommendation(
        alert_id=db_alert.id,
        risk_level=decision["risk_level"],
        recommended_action=decision["recommended_action"],
        explanation=decision["explanation"],
        rule_id=decision["rule_id"],
        requires_confirmation=decision["requires_confirmation"]
    )
    db.add(db_rec)
    
    # 4. Create AuditLog entry
    db_audit = models.AuditLog(
        alert_id=db_alert.id,
        event_type="alert_created",
        new_value=decision["recommended_action"],
        actor="system",
        reason="Initial decision engine evaluation"
    )
    db.add(db_audit)
    
    # Automatically resolve if no confirmation is required
    if not decision["requires_confirmation"]:
        db_alert.status = "auto_resolved"
        db_alert.corrective_action_at = datetime.utcnow()
        db_audit2 = models.AuditLog(
            alert_id=db_alert.id,
            event_type="status_changed",
            previous_value="pending",
            new_value="auto_resolved",
            actor="system",
            reason="Rule did not require human confirmation"
        )
        db.add(db_audit2)
    
    db.commit()
    db.refresh(db_alert)
    
    return db_alert


@router.get("", response_model=List[schemas.AlertResponse])
def get_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.excursion_detected_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=schemas.AlertDetailResponse)
def get_alert_detail(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/confirm")
def confirm_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if alert.status != "pending":
        raise HTTPException(status_code=400, detail=f"Alert cannot be confirmed (current status: {alert.status})")
        
    old_status = alert.status
    alert.status = "confirmed"
    
    now = datetime.utcnow()
    alert.confirmation_at = now
    alert.corrective_action_at = now
    
    db_audit = models.AuditLog(
        alert_id=alert.id,
        event_type="status_changed",
        previous_value=old_status,
        new_value="confirmed",
        actor="human_dispatcher",
        reason="Manual confirmation of recommendation"
    )
    db.add(db_audit)
    db.commit()
    db.refresh(alert)
    return {"status": "success", "message": "Recommendation confirmed", "alert_status": alert.status}


@router.post("/{alert_id}/override")
def override_alert(alert_id: int, override_in: schemas.OverrideCreate, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if not override_in.reason or override_in.reason.strip() == "":
        raise HTTPException(status_code=400, detail="Override reason cannot be empty")
        
    latest_rec = db.query(models.Recommendation).filter(models.Recommendation.alert_id == alert.id).order_by(models.Recommendation.recommendation_created_at.desc()).first()
    original_action = latest_rec.recommended_action if latest_rec else "unknown"
    
    old_status = alert.status
    alert.status = "overridden"
    
    now = datetime.utcnow()
    alert.confirmation_at = now
    alert.corrective_action_at = now
    
    db_override = models.Override(
        alert_id=alert.id,
        original_action=original_action,
        overridden_action=override_in.overridden_action,
        reason=override_in.reason,
        dispatcher=override_in.dispatcher
    )
    db.add(db_override)
    
    db_audit1 = models.AuditLog(
        alert_id=alert.id,
        event_type="action_overridden",
        previous_value=original_action,
        new_value=override_in.overridden_action,
        actor=override_in.dispatcher,
        reason=override_in.reason
    )
    db.add(db_audit1)
    
    db_audit2 = models.AuditLog(
        alert_id=alert.id,
        event_type="status_changed",
        previous_value=old_status,
        new_value="overridden",
        actor=override_in.dispatcher,
        reason="Action overridden by human"
    )
    db.add(db_audit2)
    
    db.commit()
    db.refresh(alert)
    
    return {"status": "success", "message": "Recommendation overridden", "alert_status": alert.status}
