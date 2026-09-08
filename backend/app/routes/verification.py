# app/routes/verification.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..database import get_db
from ..services.email_service import email_service
from ..models import Doctor, VerificationCode

router = APIRouter(prefix="/verification", tags=["verification"])

class SendCodeRequest(BaseModel):
    email: EmailStr
    purpose: str = "registration"  # "registration" ou "reset_password"

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str
    purpose: str = "registration"

class VerificationResponse(BaseModel):
    message: str
    email: str
    code: str
    purpose: str

@router.post("/send-code", response_model=VerificationResponse)
async def send_verification_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    """Envoie un code de vérification par email"""
    
    # Vérifier si l'email existe déjà pour une inscription
    if request.purpose == "registration":
        existing = db.query(Doctor).filter(Doctor.email == request.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    # Vérifier si l'email existe pour une réinitialisation de mot de passe
    if request.purpose == "reset_password":
        existing = db.query(Doctor).filter(Doctor.email == request.email).first()
        if not existing:
            raise HTTPException(status_code=400, detail="Cet email n'est pas enregistré")
    
    # Créer le code de vérification
    verification = email_service.create_verification_code(db, request.email, request.purpose)
    
    # Envoyer l'email
    await email_service.send_verification_code(request.email, verification.code, request.purpose)
    
    return {
        "message": "Code de vérification envoyé avec succès",
        "email": request.email,
        "code": verification.code,  # En production, ne pas retourner le code !
        "purpose": request.purpose
    }

@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """Vérifie un code de vérification"""
    is_valid = email_service.verify_code(db, request.email, request.code, request.purpose)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Code de vérification invalide ou expiré")
    
    return {"message": "Code vérifié avec succès", "email": request.email, "verified": True, "purpose": request.purpose}