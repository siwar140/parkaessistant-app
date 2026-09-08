# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    hospital = Column(String(255), nullable=True)
    specialty = Column(String(255), nullable=True)
    profile_image = Column(String(500), nullable=True)  # ✅ Nouveau champ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patients = relationship("Patient", back_populates="doctor", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="doctor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Doctor(id={self.id}, email={self.email}, full_name={self.full_name})>"