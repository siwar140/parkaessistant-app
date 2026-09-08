# app/models/prediction.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=True)
    patient_name = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    result = Column(String(50), nullable=False)  # "Sain" ou "Malade"
    probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    duration = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    doctor = relationship("Doctor", back_populates="predictions")
    patient = relationship("Patient", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, result={self.result}, probability={self.probability})>"