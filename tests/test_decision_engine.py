import pytest
from backend.services.decision_engine import evaluate_excursion

def test_normal_temperature():
    # Scenario 1: normal temperature (R001)
    res = evaluate_excursion(
        temperature_c=-18.0, 
        duration_minutes=10, 
        location="warehouse", 
        product_class="frozen", 
        available_actions=["continue_monitoring"]
    )
    assert res["rule_id"] == "R001"
    assert res["risk_level"] == "LOW"
    assert res["recommended_action"] == "continue_monitoring"

def test_moderate_excursion():
    # Scenario 2: moderate excursion (R002)
    res = evaluate_excursion(
        temperature_c=-12.0, 
        duration_minutes=20, 
        location="warehouse", 
        product_class="frozen", 
        available_actions=["move_to_controlled_storage"]
    )
    assert res["rule_id"] == "R002"
    assert res["risk_level"] == "MEDIUM"
    assert res["recommended_action"] == "move_to_controlled_storage"

def test_severe_excursion():
    # Scenario 3: severe excursion (R003)
    res = evaluate_excursion(
        temperature_c=10.0, 
        duration_minutes=20, 
        location="warehouse", 
        product_class="chilled", 
        available_actions=["quarantine"]
    )
    assert res["rule_id"] == "R003"
    assert res["risk_level"] == "HIGH"
    assert res["recommended_action"] == "quarantine"

def test_unknown_product_class():
    # Scenario 4: unknown product class (R004)
    res = evaluate_excursion(
        temperature_c=2.0, 
        duration_minutes=10, 
        location="warehouse", 
        product_class="produce", 
        available_actions=["quarantine"]
    )
    assert res["rule_id"] == "R004"
    assert res["risk_level"] == "HIGH"
    assert res["recommended_action"] == "quarantine"

def test_unavailable_recommended_action():
    # Scenario 5: unavailable recommended action (R005)
    # The moderate temp should trigger R002 (move_to_controlled_storage), 
    # but since it's not in available_actions, it falls back (R005).
    res = evaluate_excursion(
        temperature_c=-12.0, 
        duration_minutes=20, 
        location="warehouse", 
        product_class="frozen", 
        available_actions=["continue_monitoring", "quarantine"]
    )
    assert "R005" in res["rule_id"]
    assert res["recommended_action"] == "quarantine"

def test_missing_data():
    # Scenario 6: missing data (R007)
    res = evaluate_excursion(
        temperature_c=None, 
        duration_minutes=20, 
        location="warehouse", 
        product_class="frozen", 
        available_actions=["escalate_to_supervisor"]
    )
    assert res["rule_id"] == "R007"
    assert res["risk_level"] == "HIGH"
    assert res["recommended_action"] == "escalate_to_supervisor"

def test_customer_delivery_scenario():
    # Scenario 7: customer delivery scenario (R006)
    res = evaluate_excursion(
        temperature_c=10.0, 
        duration_minutes=20, 
        location="customer_delivery", 
        product_class="chilled", 
        available_actions=["dispatch_replacement"]
    )
    assert res["rule_id"] == "R006"
    assert res["recommended_action"] == "dispatch_replacement"
    assert res["risk_level"] == "HIGH"
