# app/routes/doctor.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os, uuid, shutil
from ..database import get_db
from ..models import Doctor
from ..schemas import DoctorResponse, DoctorUpdate, DoctorPasswordUpdate
from ..auth import get_current_doctor, get_password_hash, verify_password
from ..config import settings

router = APIRouter(prefix="/doctor", tags=["doctor"])

@router.get("/profile", response_model=DoctorResponse)
async def get_profile(current_doctor: Doctor = Depends(get_current_doctor)):
    return current_doctor

@router.put("/profile", response_model=DoctorResponse)
async def update_profile(
    update: DoctorUpdate,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    if update.full_name is not None:
        current_doctor.full_name = update.full_name
    if update.phone is not None:
        current_doctor.phone = update.phone
    if update.hospital is not None:
        current_doctor.hospital = update.hospital
    if update.specialty is not None:
        current_doctor.specialty = update.specialty
    
    db.commit()
    db.refresh(current_doctor)
    return current_doctor

@router.put("/password")
async def update_password(
    update: DoctorPasswordUpdate,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    if not verify_password(update.old_password, current_doctor.hashed_password):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
    
    current_doctor.hashed_password = get_password_hash(update.new_password)
    db.commit()
    db.refresh(current_doctor)
    
    return {"message": "Mot de passe mis à jour avec succès"}

@router.put("/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """Upload la photo de profil depuis le local"""
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez JPEG, PNG ou WEBP")
    
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    if not file_extension:
        file_extension = '.jpg'
    
    upload_dir = os.path.join(settings.UPLOAD_DIR, 'profiles')
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    if current_doctor.profile_image and os.path.exists(current_doctor.profile_image):
        try:
            os.remove(current_doctor.profile_image)
        except:
            pass
    
    current_doctor.profile_image = file_path
    db.commit()
    db.refresh(current_doctor)
    
    return {"message": "Photo de profil mise à jour", "profile_image": file_path}

@router.get("/profile-image/{doctor_id}")
async def get_profile_image(doctor_id: int, db: Session = Depends(get_db)):
    """Récupère la photo de profil d'un médecin"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    
    if not doctor or not doctor.profile_image:
        raise HTTPException(status_code=404, detail="Photo de profil non trouvée")
    
    if not os.path.exists(doctor.profile_image):
        raise HTTPException(status_code=404, detail="Photo de profil non trouvée")
    
    return FileResponse(doctor.profile_image)