# ColdChain Assist - Metrics and Analysis

## Baseline
Historically, in manual warehouse and dispatch operations, it takes approximately **15 minutes** from the moment a temperature excursion is detected via telemetry for a dispatcher to manually:
1. Locate the item data
2. Cross-reference complex product thresholds
3. Make and log a corrective decision
*Note: This baseline value is a realistic operational assumption simulated for the purposes of benchmarking this prototype.*

## Target and Benchmark
The goal of the decision-support system is to reduce the time from excursion detection to initiating the correct corrective action to a target value (default 5 minutes).
This benchmark is configurable in the UI. Users can adjust the Baseline Response Time (e.g., 15 minutes) and Target Response Time (e.g., 5 minutes) to see calculated improvements dynamically based on valid operational metrics.

## Measured Result
The prototype calculates actual system performance based on database timestamps (time from excursion detection to corrective action confirmation). The dashboard explicitly contrasts the baseline vs the target against the live measured response-time metric to compute improvement percentages.

### Specific Time Metrics Tracked
- **time-to-recommendation:** The time between the excursion detection (`excursion_detected_at`) and when the engine generated the recommendation (`recommendation_created_at`).
- **time-to-confirmation:** The time between excursion detection and when a human manually confirmed the action (`confirmation_at`).
- **time-to-corrective-action:** The total time from excursion detection until the final resolution (`corrective_action_at`), combining automated processing and human delay.

## Error Analysis & Trade-offs
- **Incorrect recommendations:** Tracked via Dispatcher Overrides.
- **False-safe decisions:** Tracked via Audit Logs (human overriding LOW risk to HIGH risk).
- **Unnecessary escalations:** Overriding an escalation down to `continue_monitoring`.
- **Unavailable-action cases:** Triggered when R005 fallback logic is invoked.

*Efficiency, Safety, Fairness, and Customer Service are inherently balanced by deterministic rules, defaulting to extreme safety in uncertain edge cases.*
