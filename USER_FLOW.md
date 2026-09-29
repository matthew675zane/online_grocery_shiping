# User Flows

## Primary Alert Resolution Flow

1. **Alert detected:** Telemetry data (temperature, duration, location, product class) is submitted to the API.
2. **Data validation:** FastAPI and Pydantic validate the request payload. If invalid, it rejects immediately.
3. **Risk evaluation:** The Decision Engine processes the data against configured thresholds.
4. **Recommendation:** The engine returns a structured recommendation (action, risk, rule ID, explanation).
5. **Explanation:** The frontend displays the recommendation clearly to the dispatcher, explaining exactly why it was chosen.
6. **Human confirmation:** If the engine flags the risk as HIGH, the workflow halts. The dispatcher reviews the explanation and clicks "Confirm".
7. **Corrective action:** The physical corrective action is initiated (e.g., product moved to quarantine).
8. **Audit log:** The system automatically logs the confirmation, recording the dispatcher's action and timestamp.

## Dispatcher Override Flow

1. **Review Automated Decision:** A dispatcher reviews a pending alert and disagrees with the automated recommendation (e.g., due to physical package damage not visible to sensors). This acts as a critical human-in-the-loop validation for HIGH and CRITICAL risks.
2. **Initiate Override:** The dispatcher selects a new corrective action from the dropdown on the dashboard.
3. **Provide Justification:** The dispatcher selects a structured Reason Code (e.g., "Packaging unavailable", "Customer priority") and may optionally type a free-text explanation for additional context. If "Other" is selected, the explanation is mandatory.
4. **Submit Override:** The API processes the request.
5. **Audit Logging:** The system preserves the original automated recommendation, creates an Override record, and inserts a detailed Audit Log linking the human actor, the old action, the new action, and the specific reason code and context. The alert status is moved to `overridden`.
