# Validation Strategy

## Validation Dataset
The system utilizes a static, meticulously constructed validation dataset (`data/validation_dataset.csv`) containing 30 deterministic test cases.

## Test Methodology
A standalone validation runner (`tests/run_validation.py`) iterates through the CSV, injects the parameters directly into the Decision Engine, and compares the actual output to the strictly defined expected output. 

## Test Cases
The dataset balances multiple variables:
- **Temperature:** Normal, mildly outside range, significantly outside range, extreme.
- **Duration:** Short, medium, prolonged.
- **Locations:** Warehouse, loading area, vehicle, customer delivery.
- **Product Classes:** Frozen, chilled, unknown.

## Accuracy
The engine currently scores **100.0%** accuracy on perfect action matching against the validation dataset.

## Edge-Case Performance
The dataset includes specific boundary cases (EDGE-01 to EDGE-06), testing missing temperatures, missing durations, unknown classes, and optimal action unavailability. The edge-case pass rate is **100%**.

## False-Safe Decisions
The engine scored **0** false-safe decisions. (A critical error where a high-risk situation is dangerously evaluated as low risk).

## False Escalation
The engine scored **0** false-escalation decisions. (An efficiency error where a perfectly normal temperature is unnecessarily escalated to quarantine).

## Error Analysis
If future validation tests fail, the runner automatically categorizes failures into false-safes, false-escalations, or action mismatches to rapidly assist developers in debugging rule logic.
