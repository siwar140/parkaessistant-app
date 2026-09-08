# app/models/__init__.py
from .user import Doctor
from .patient import Patient
from .prediction import Prediction
from .verification import VerificationCode

__all__ = ["Doctor", "Patient", "Prediction", "VerificationCode"]