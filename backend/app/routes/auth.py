# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..schemas import LoginRequest, LoginResponse, RegisterRequest, DoctorResponse, ResetPasswordRequest
from ..auth import authenticate_user, create_access_token, get_password_hash
from ..models import Doctor
from ..services.email_service import email_service
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=DoctorResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Inscription d'un nouveau médecin"""
    existing = db.query(Doctor).filter(Doctor.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    hashed_password = get_password_hash(request.password)
    doctor = Doctor(
        email=request.email,
        hashed_password=hashed_password,
        full_name=request.full_name,
        phone=request.phone,
        hospital=request.hospital,
        specialty=request.specialty
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Connexion d'un médecin"""
    doctor = authenticate_user(db, request.email, request.password)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(doctor.id)}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "doctor": doctor}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Réinitialise le mot de passe après vérification du code"""
    # Vérifier si le code est valide
    is_valid = email_service.verify_code(db, request.email, request.code, "reset_password")
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de vérification invalide ou expiré"
        )
    
    # Vérifier si le médecin existe
    doctor = db.query(Doctor).filter(Doctor.email == request.email).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médecin non trouvé"
        )
    
    # Mettre à jour le mot de passe
    doctor.hashed_password = get_password_hash(request.new_password)
    db.commit()
    db.refresh(doctor)
    
    return {"message": "Mot de passe réinitialisé avec succès"}