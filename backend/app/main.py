# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import auth, doctor, patients, prediction, verification
from .config import settings
from .ml_inference import load_model_once
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="API pour la détection de la maladie de Parkinson via l'analyse vocale",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(auth.router, prefix="/api")
app.include_router(doctor.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(prediction.router, prefix="/api")
app.include_router(verification.router, prefix="/api")

@app.on_event("startup")
async def startup():
    init_db()
    try:
        load_model_once()
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement du modèle: {e}")

@app.get("/")
async def root():
    return {"message": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}