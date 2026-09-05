# ColdChain Assist - Requirements

## Problem Statement
In online grocery shipping, frozen and chilled products are often shipped together. When temperature excursions occur during operations or delivery, staff must quickly determine the safest and most efficient corrective action. Relying solely on manual processes for cross-referencing product thresholds and available actions is slow, prone to inconsistency, and risks compromising food safety.

## Users
1. **Warehouse/Loading Area Staff:** Personnel handling the physical items prior to dispatch.
2. **Dispatchers:** Operators reviewing high-risk alerts and confirming or overriding automated recommendations.
3. **Delivery Drivers:** Personnel executing corrective actions (e.g., dispatching replacements) at the customer delivery stage.
4. **Supervisors/Managers:** Reviewers analyzing audit logs and operational metrics.

## Functional Requirements
- The system must evaluate temperature excursions based on temperature, duration, location, product class, and available actions.
- The system must provide a recommended corrective action alongside a risk level.
- The system must support customer-delivery specific logic (e.g., dispatching replacements).
- The system must enforce fallback logic if the ideal corrective action is unavailable.

## Non-Functional Requirements
- Must provide clear API endpoints via FastAPI.
- Must present a clean, professional, enterprise-grade Streamlit dashboard.
- Must operate deterministically without relying on unpredictable machine learning models.

## Safety Requirements
- High-risk or uncertain cases must not be silently approved.
- Any missing critical data (temperature, duration) must immediately trigger an escalation to a supervisor.
- Unknown product classes must default to quarantine.

## Explainability Requirements
- Every automated recommendation must include a human-readable explanation of "Why this action?"
- Every recommendation must explicitly reference the internal Rule ID used to make the decision.

## Human Confirmation Requirements
- Actions flagged as HIGH risk or uncertain require explicit human confirmation before the alert is considered resolved.
- LOW risk actions may be auto-resolved to save operational time.

## Dispatcher Override Requirements
- Dispatchers must be able to override an automated recommendation.
- An override absolutely requires a non-empty text justification and the dispatcher's name.

## Audit Requirements
- Every state change, automated recommendation, confirmation, and override must be immutably logged.
- The audit log must record the previous value, new value, reason, actor, and exact timestamp.

## Metrics Requirements
- The system must track average time-to-recommendation, time-to-confirmation, and time-to-corrective-action.
- Metrics must be calculated dynamically from actual database timestamps, not fabricated.
- The system must track total overrides, edge cases, and resolution status counts.
