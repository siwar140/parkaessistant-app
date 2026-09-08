# app/routes/patients.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..models import Doctor, Patient, Prediction
from ..schemas import PatientResponse, PatientCreate, PatientUpdate
from ..auth import get_current_doctor

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("", response_model=List[PatientResponse])
async def get_patients(
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(default=None),
):
    query = db.query(Patient).filter(Patient.doctor_id == current_doctor.id)
    if search:
        query = query.filter(
            or_(
                Patient.first_name.ilike(f"%{search}%"),
                Patient.last_name.ilike(f"%{search}%"),
                Patient.email.ilike(f"%{search}%"),
            )
        )
    return query.order_by(Patient.created_at.desc()).all()

@router.post("", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    new_patient = Patient(
        doctor_id=current_doctor.id,
        **patient.dict(),
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == current_doctor.id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    patient.predictions = db.query(Prediction).filter(
        Prediction.patient_id == patient.id
    ).order_by(Prediction.created_at.desc()).all()
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    update: PatientUpdate,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == current_doctor.id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.doctor_id == current_doctor.id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    db.delete(patient)
    db.commit()
    return {"message": "Patient supprimé"}