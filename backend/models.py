from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    location = Column(String, index=True)
    product_class = Column(String)
    packaging_condition = Column(String, default="intact", nullable=True)
    cooling_source_proximity = Column(String, default="separated", nullable=True)
    mixed_load = Column(Boolean, default=False, nullable=True)
    available_actions = Column(JSON)
    
    # Timestamps
    excursion_detected_at = Column(DateTime, default=datetime.utcnow)
    confirmation_at = Column(DateTime, nullable=True)
    corrective_action_at = Column(DateTime, nullable=True)
    
    status = Column(String, default="pending")

    # Relationships
    recommendations = relationship("Recommendation", back_populates="alert")
    overrides = relationship("Override", back_populates="alert")
    audit_logs = relationship("AuditLog", back_populates="alert")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    risk_level = Column(String)
    recommended_action = Column(String)
    explanation = Column(String)
    rule_id = Column(String)
    requires_confirmation = Column(Boolean, default=False)
    recommendation_created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    alert = relationship("Alert", back_populates="recommendations")


class Override(Base):
    __tablename__ = "overrides"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    original_action = Column(String)
    overridden_action = Column(String)
    reason_code = Column(String)
    explanation = Column(String, nullable=True)
    dispatcher = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    alert = relationship("Alert", back_populates="overrides")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    event_type = Column(String, index=True)
    previous_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    actor = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    alert = relationship("Alert", back_populates="audit_logs")
