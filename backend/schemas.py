from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AlertCreate(BaseModel):
    temperature: Optional[float] = None
    duration_minutes: Optional[int] = None
    location: str
    product_class: str
    packaging_condition: Optional[str] = "intact"
    cooling_source_proximity: Optional[str] = "separated"
    mixed_load: Optional[bool] = False
    available_actions: List[str]

class RecommendationResponse(BaseModel):
    id: int
    alert_id: int
    risk_level: str
    recommended_action: str
    explanation: str
    rule_id: str
    requires_confirmation: bool
    recommendation_created_at: datetime
    
    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    previous_value: Optional[str]
    new_value: Optional[str]
    reason: Optional[str]
    actor: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    temperature: Optional[float]
    duration_minutes: Optional[int]
    location: str
    product_class: str
    packaging_condition: Optional[str] = None
    cooling_source_proximity: Optional[str] = None
    mixed_load: Optional[bool] = None
    available_actions: List[str]
    excursion_detected_at: datetime
    confirmation_at: Optional[datetime]
    corrective_action_at: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True

class AlertDetailResponse(AlertResponse):
    recommendations: List[RecommendationResponse] = []
    audit_logs: List[AuditLogResponse] = []

class OverrideCreate(BaseModel):
    overridden_action: str
    reason_code: str
    explanation: Optional[str] = None
    dispatcher: str
