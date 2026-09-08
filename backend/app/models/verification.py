# app/models/verification.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from ..database import Base

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    code = Column(String(6), nullable=False)
    purpose = Column(String(20), default="registration")  # "registration" ou "reset_password"
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<VerificationCode(email={self.email}, code={self.code}, purpose={self.purpose}, is_used={self.is_used})>"