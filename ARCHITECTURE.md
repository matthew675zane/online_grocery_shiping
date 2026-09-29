# System Architecture

The ColdChain Assist prototype follows a clean, decoupled, API-first architecture designed for rapid prototyping and traceability.

## System Architecture Overview
The system is divided into a backend API layer responsible for data persistence and logic, and a frontend presentation layer for user interaction.

## Frontend
- **Technology:** Streamlit
- **Role:** Provides a professional, clean, interactive dashboard. It communicates exclusively via REST HTTP calls to the backend API.
- **Components:** Executive Dashboard, Alert Creation Simulation, Alert Management (Confirmation/Overrides), Metrics, Rule Reference, Safety Controls, and Audit History.

## Backend
- **Technology:** FastAPI (Python 3)
- **Role:** Handles routing, input validation, and orchestrates the database interactions and decision engine execution.

## API
- **Endpoints:** RESTful API under `/api/alerts` and `/api/metrics`.
- **Validation:** Utilizes Pydantic schemas to strongly type and validate all incoming requests and outgoing responses.

## Decision Engine
- **Role:** A pure Python, deterministic, rule-based service (`backend/services/decision_engine.py`).
- **Function:** Takes sanitized excursion data and applies operational rules (R001-R007) to compute a risk level, recommended action, and explanation. It avoids machine learning to ensure 100% explainability.

## Database
- **Technology:** SQLite with SQLAlchemy ORM.
- **Structure:** Relational structure containing `Alerts` (parent), `Recommendations` (1:N), `Overrides` (1:N), and `AuditLogs` (1:N).

## Validation Layer
- **Role:** A standalone script (`tests/run_validation.py`) and static dataset (`data/validation_dataset.csv`).
- **Function:** Ensures the decision engine behaves with 100% accuracy against 30 strictly defined edge cases.

## Audit Layer
- **Role:** Database and API mechanisms that trap every state transition.
- **Function:** Records the `event_type`, `previous_value`, `new_value`, `actor`, and `reason` for full compliance tracking.
- **Immutable Plan-Change History:** Every change, confirmation, or override creates an immutable audit record. Historical decisions are never overwritten, ensuring we can always answer: "What was recommended?", "What did the dispatcher do?", "When did they do it?", and "Why was it changed?".

## Metrics Layer
- **Role:** Service module (`backend/services/metrics_service.py`).
- **Function:** Dynamically calculates operational efficiency by extracting true timestamps from the Audit and Alert layers to compute `time-to-corrective-action`.
