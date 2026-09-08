# app/config.py
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Parkinson Voice Detection API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./parkinson.db"
    
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    
    MODEL_PATH: str = "./models_ia/parkinson_cnn+aug_off_weights_bst.h5"
    MODEL_KERAS_PATH: str = "./models_ia/parkinson_model.keras"
    
    # Configuration Resend
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "no-reply@parkimvoice.tn"
    RESEND_FROM_NAME: str = "ParkimVoice Diagnosis Assistant"
    
    # Vérification
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" 

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)