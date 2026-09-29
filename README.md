# Cold-Chain Alert Assistant

A Field-Ready Prototype for Online Grocer Shipping Frozen and Chilled Items Together.

## Project Overview
ColdChain Assist is a prototype decision-support system designed to help dispatch and warehouse staff rapidly and safely respond to temperature excursions. By evaluating telemetry against configured safety rules, it provides deterministic, explainable recommendations while ensuring high-risk scenarios always require human confirmation.

## Architecture
The project uses a decoupled architecture:
- **Backend:** FastAPI (Python 3) handling REST API, data validation (Pydantic), and the decision engine.
- **Frontend:** Streamlit providing a professional enterprise dashboard.
- **Database:** SQLite with SQLAlchemy ORM logging state changes and audit histories.

## Features
- Deterministic, explainable Decision Engine.
- Advanced Frozen/Chilled Co-Shipping Rules: Identifies mixed-load conflicts, chilled item freezing risks (due to proximity to dry ice or temperatures), and frozen item thawing risks (due to inadequate insulation).
- End-to-end Audit Logging for total transparency.
- Mandatory text rationale for Dispatcher Overrides.
- Live performance metrics calculating Time-to-Corrective-Action.

## Setup
```bash
# Clone the repository and setup the virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Backend Startup
Run the FastAPI backend server:
```bash
source venv/bin/activate
uvicorn backend.main:app --reload
```
The API and interactive docs will be available at `http://127.0.0.1:8000/docs`.

## Frontend Startup
In a separate terminal, run the Streamlit dashboard:
```bash
source venv/bin/activate
streamlit run frontend/app.py
```

## API Endpoints
- `GET /health` - System health check
- `POST /api/alerts` - Create a new alert and run the decision engine
- `GET /api/alerts` - Retrieve recent alerts
- `GET /api/alerts/{alert_id}` - View specific alert history
- `POST /api/alerts/{alert_id}/confirm` - Confirm a high-risk recommendation
- `POST /api/alerts/{alert_id}/override` - Override a recommendation (requires rationale)
- `GET /api/metrics` - Retrieve system performance metrics

## Testing
To test the environment or logic, ensure pytest is installed.

## Validation
The engine is validated against a rigorous 30-case dataset ensuring perfect handling of edge cases, false-safes, and unknown variables.
```bash
python3 tests/run_validation.py
```

## Screenshots
*(Screenshot placeholder - Insert dashboard images here)*

## Limitations
This system is an experimental prototype. **It does not guarantee food safety and claims no regulatory certification.** It requires domain expert validation and real operational data before production deployment. See `LIMITATIONS.md` for more details.

## Future Work
Refer to `PROJECT_STATUS.md` for a comprehensive list of pending features, including IoT ingestion, PostgreSQL migration, and role-based access control.
