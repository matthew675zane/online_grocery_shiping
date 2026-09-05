from typing import List, Optional, Dict, Any

# Configurable thresholds for the prototype decision engine.
THRESHOLDS = {
    "frozen": {
        "min_safe_temp": -50.0,
        "max_safe_temp": -15.0,
        "critical_max_temp": -10.0,  # Above -10 is considered severe
    },
    "chilled": {
        "min_safe_temp": 1.0,
        "max_safe_temp": 5.0,
        "critical_max_temp": 8.0,      # Above 8 is considered severe
        "critical_min_temp": -0.5,     # Below -0.5 is considered severe freezing
    },
    "durations": {
        "moderate_limit": 15,  # minutes
        "severe_limit": 60     # minutes
    }
}

VALID_PRODUCT_CLASSES = ["frozen", "chilled"]

def _get_fallback_action(desired_action: str, available_actions: List[str]) -> tuple[str, str]:
    """
    Determines the safest fallback action if the desired one is unavailable.
    Priority order: quarantine > move_to_controlled_storage > escalate_to_supervisor > inspect_packaging > continue_monitoring
    """
    safe_order = [
        "quarantine",
        "move_to_controlled_storage",
        "escalate_to_supervisor",
        "inspect_packaging",
        "continue_monitoring"
    ]
    
    for action in safe_order:
        if action in available_actions:
            return action, f"Original action '{desired_action}' unavailable. Selected fallback: '{action}'."
            
    if "escalate_to_supervisor" in available_actions:
        return "escalate_to_supervisor", "No safe alternative found. Escalating."
    elif available_actions:
        return available_actions[0], "Falling back to the first available action."
        
    return "escalate_to_supervisor", "No available actions. Implicitly escalating."


def evaluate_excursion(
    temperature_c: Optional[float],
    duration_minutes: Optional[int],
    location: Optional[str],
    product_class: Optional[str],
    available_actions: List[str]
) -> Dict[str, Any]:
    """
    Evaluates a cold-chain excursion and provides a recommendation.
    NOTE: This is a decision-support prototype and does not guarantee food safety.
    """
    
    # Base recommendation structure
    rec = {
        "risk_level": "UNKNOWN",
        "recommended_action": "escalate_to_supervisor",
        "explanation": "",
        "rule_id": "",
        "requires_confirmation": True,
        "confidence": "HIGH",
        "safety_notes": "This is a decision-support prototype. It does not guarantee food safety. Do not use for regulatory compliance without human validation."
    }
    
    def finalize(action: str, explanation: str, risk: str, rule: str, confirm: bool):
        if action not in available_actions:
            # Rule R005: Fallback if action is unavailable
            fallback, fb_explanation = _get_fallback_action(action, available_actions)
            rec["recommended_action"] = fallback
            rec["explanation"] = f"{explanation} | {fb_explanation}"
            rec["rule_id"] = f"{rule} -> R005"
            rec["risk_level"] = risk
            rec["requires_confirmation"] = True
        else:
            rec["recommended_action"] = action
            rec["explanation"] = explanation
            rec["rule_id"] = rule
            rec["risk_level"] = risk
            rec["requires_confirmation"] = confirm

    # RULE R007: Missing or contradictory data
    if temperature_c is None or duration_minutes is None:
        finalize(
            action="escalate_to_supervisor",
            explanation="Critical data (temperature or duration) is missing.",
            risk="HIGH",
            rule="R007",
            confirm=True
        )
        return rec

    # RULE R004: Unknown product class
    if product_class not in VALID_PRODUCT_CLASSES:
        finalize(
            action="quarantine",
            explanation=f"Product class '{product_class}' is unknown.",
            risk="HIGH",
            rule="R004",
            confirm=True
        )
        return rec

    thresholds = THRESHOLDS[product_class]
    
    # Evaluate temperature severity
    is_severe_temp = False
    is_moderate_temp = False
    
    if product_class == "frozen":
        if temperature_c > thresholds["critical_max_temp"]:
            is_severe_temp = True
        elif temperature_c > thresholds["max_safe_temp"]:
            is_moderate_temp = True
    elif product_class == "chilled":
        if temperature_c > thresholds["critical_max_temp"] or temperature_c < thresholds["critical_min_temp"]:
            is_severe_temp = True
        elif temperature_c > thresholds["max_safe_temp"] or temperature_c < thresholds["min_safe_temp"]:
            is_moderate_temp = True

    # Evaluate duration severity
    is_prolonged = duration_minutes >= THRESHOLDS["durations"]["severe_limit"]
    
    is_excursion = is_severe_temp or is_moderate_temp
    
    # RULE R006: Customer delivery impact
    if location == "customer_delivery" and is_excursion:
        finalize(
            action="dispatch_replacement",
            explanation="Excursion occurred at customer delivery. Prioritize replacement for customer satisfaction.",
            risk="HIGH" if is_severe_temp or is_prolonged else "MEDIUM",
            rule="R006",
            confirm=True
        )
        return rec

    # RULE R003: Severe or prolonged excursion
    if is_severe_temp or is_prolonged:
        finalize(
            action="quarantine",
            explanation="The excursion is severe or prolonged.",
            risk="HIGH",
            rule="R003",
            confirm=True
        )
        return rec

    # RULE R002: Moderate excursion
    if is_moderate_temp:
        finalize(
            action="move_to_controlled_storage",
            explanation="Temperature is outside the acceptable range for a moderate duration.",
            risk="MEDIUM",
            rule="R002",
            confirm=False
        )
        return rec

    # RULE R001: Normal temperature (within acceptable range)
    finalize(
        action="continue_monitoring",
        explanation="Temperature is within the configured acceptable range for the product class.",
        risk="LOW",
        rule="R001",
        confirm=False
    )
    return rec
