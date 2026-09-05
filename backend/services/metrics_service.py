from sqlalchemy.orm import Session
from .. import models

def calculate_metrics(db: Session):
    total_alerts = db.query(models.Alert).count()
    
    low_risk = db.query(models.Recommendation).filter(models.Recommendation.risk_level == "LOW").count()
    medium_risk = db.query(models.Recommendation).filter(models.Recommendation.risk_level == "MEDIUM").count()
    high_risk = db.query(models.Recommendation).filter(models.Recommendation.risk_level == "HIGH").count()
    
    confirmed = db.query(models.Alert).filter(models.Alert.status == "confirmed").count()
    overrides = db.query(models.Override).count()
    
    alerts = db.query(models.Alert).all()
    
    total_time_to_rec = 0
    total_time_to_conf = 0
    total_time_to_action = 0
    
    count_rec = 0
    count_conf = 0
    count_action = 0
    
    for alert in alerts:
        # Latest recommendation
        rec = db.query(models.Recommendation).filter(models.Recommendation.alert_id == alert.id).order_by(models.Recommendation.id.desc()).first()
        if rec and alert.excursion_detected_at:
            diff_rec = (rec.recommendation_created_at - alert.excursion_detected_at).total_seconds()
            total_time_to_rec += diff_rec
            count_rec += 1
            
        if alert.confirmation_at and alert.excursion_detected_at:
            diff_conf = (alert.confirmation_at - alert.excursion_detected_at).total_seconds()
            total_time_to_conf += diff_conf
            count_conf += 1
            
        if alert.corrective_action_at and alert.excursion_detected_at:
            diff_action = (alert.corrective_action_at - alert.excursion_detected_at).total_seconds()
            total_time_to_action += diff_action
            count_action += 1
            
    avg_rec_sec = total_time_to_rec / count_rec if count_rec > 0 else 0
    avg_conf_sec = total_time_to_conf / count_conf if count_conf > 0 else 0
    avg_action_sec = total_time_to_action / count_action if count_action > 0 else 0
    
    # Error Analysis
    unavailable_action_cases = db.query(models.Recommendation).filter(models.Recommendation.rule_id.like("%R005%")).count()
    
    def format_time(seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}m {s}s"
    
    return {
        "total_alerts": total_alerts,
        "low_risk_alerts": low_risk,
        "medium_risk_alerts": medium_risk,
        "high_risk_alerts": high_risk,
        "confirmed_recommendations": confirmed,
        "overrides": overrides,
        "avg_time_to_recommendation": format_time(avg_rec_sec),
        "avg_time_to_confirmation": format_time(avg_conf_sec),
        "average_time_to_corrective_action": format_time(avg_action_sec),
        "avg_time_to_corrective_action_sec": avg_action_sec,
        "unavailable_action_cases": unavailable_action_cases
    }
