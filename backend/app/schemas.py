# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ============ AUTH ============
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    doctor: "DoctorResponse"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    hospital: Optional[str] = None
    specialty: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

# ============ DOCTOR ============
class DoctorResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    hospital: Optional[str] = None
    specialty: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    hospital: Optional[str] = None
    specialty: Optional[str] = None

class DoctorPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# ============ PATIENT ============
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    notes: Optional[str] = None

class PatientResponse(PatientBase):
    id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime
    predictions: List["PredictionResponse"] = []

    class Config:
        from_attributes = True

# ============ PREDICTION ============
class PredictionResult(BaseModel):
    result: str
    confidence: float
    probability: float
    patient_name: Optional[str] = None
    patient_id: Optional[int] = None

class PredictionResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    file_name: str
    file_path: Optional[str] = None
    result: str
    probability: float
    confidence: float
    duration: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============ VERIFICATION ============
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

# Pour éviter les importations circulaires
DoctorResponse.model_rebuild()
PatientResponse.model_rebuild()
PredictionResponse.model_rebuild()
# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ============ DOCTOR ============
class DoctorResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    hospital: Optional[str] = None
    specialty: Optional[str] = None
    profile_image: Optional[str] = None  # ✅ Nouveau champ
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    hospital: Optional[str] = None
    specialty: Optional[str] = None
    profile_image: Optional[str] = None  # ✅ Nouveau champ