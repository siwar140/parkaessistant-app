# app/routes/prediction.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import os, uuid, shutil
from typing import Optional, List
from ..database import get_db
from ..models import Doctor, Patient, Prediction
from ..schemas import PredictionResponse, PredictionResult
from ..auth import get_current_doctor
from ..ml_inference import predict_file
from ..config import settings

router = APIRouter(prefix="/predictions", tags=["predictions"])

ALLOWED_CONTENT_TYPES = {
    'audio/wav': '.wav',
    'audio/x-wav': '.wav',
    'audio/mpeg': '.mp3',
    'audio/mp3': '.mp3',
    'audio/ogg': '.ogg',
    'application/ogg': '.ogg'
}

@router.post("/analyze", response_model=PredictionResult)
async def analyze_audio(
    file: UploadFile = File(...),
    patient_id: Optional[int] = Form(None),
    patient_name: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Format de fichier non supporté. Utilisez WAV, MP3 ou OGG.")
    
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    if not file_extension:
        file_extension = ALLOWED_CONTENT_TYPES[file.content_type]
    
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_extension}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = predict_file(file_path)
        
        patient = None
        patient_name_final = patient_name
        
        if patient_id:
            patient = db.query(Patient).filter(
                Patient.id == patient_id,
                Patient.doctor_id == current_doctor.id
            ).first()
            if patient:
                patient_name_final = f"{patient.first_name} {patient.last_name}"
        
        if not patient and patient_name:
            parts = patient_name.split()
            first_name = parts[0] if parts else "Inconnu"
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
            existing = db.query(Patient).filter(
                Patient.doctor_id == current_doctor.id,
                Patient.first_name.ilike(first_name),
                Patient.last_name.ilike(last_name)
            ).first()
            if not existing:
                patient = Patient(
                    doctor_id=current_doctor.id,
                    first_name=first_name,
                    last_name=last_name,
                    notes="Créé automatiquement lors de l'analyse"
                )
                db.add(patient)
                db.commit()
                db.refresh(patient)
            else:
                patient = existing
                patient_name_final = patient_name
        
        prediction = Prediction(
            doctor_id=current_doctor.id,
            patient_id=patient.id if patient else None,
            patient_name=patient_name_final,
            file_name=file.filename,
            file_path=file_path,
            result=result["result"],
            probability=result["probability"],
            confidence=result["confidence"],
            notes=notes,
            created_at=datetime.utcnow()
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        return {
            **result,
            "patient_name": patient_name_final,
            "patient_id": patient.id if patient else None
        }
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

@router.get("/history", response_model=List[PredictionResponse])
async def get_history(
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
    patient_id: Optional[int] = None
):
    query = db.query(Prediction).filter(Prediction.doctor_id == current_doctor.id)
    if patient_id:
        query = query.filter(Prediction.patient_id == patient_id)
    return query.order_by(Prediction.created_at.desc()).all()

@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.doctor_id == current_doctor.id
    ).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    return prediction

@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.doctor_id == current_doctor.id
    ).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    if prediction.file_path and os.path.exists(prediction.file_path):
        try:
            os.remove(prediction.file_path)
        except:
            pass
    db.delete(prediction)
    db.commit()
    return {"message": "Analyse supprimée"}