from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routes import alerts, metrics

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cold-Chain Alert Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router)
app.include_router(metrics.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}
