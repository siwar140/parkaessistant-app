# app/services/email_service.py
import requests
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import VerificationCode
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service d'envoi d'emails avec Resend API"""
    
    @staticmethod
    async def send_verification_code(email: str, code: str, purpose: str = "registration"):
        """Envoie un code de vérification par email"""
        try:
            # Déterminer le sujet selon le but
            if purpose == "registration":
                subject = f"Code de vérification ParkimVoice - {code}"
                message_intro = "Voici votre code de vérification pour créer votre compte :"
            elif purpose == "reset_password":
                subject = f"Code de réinitialisation ParkimVoice - {code}"
                message_intro = "Voici votre code pour réinitialiser votre mot de passe :"
            else:
                subject = f"Code de vérification ParkimVoice - {code}"
                message_intro = "Voici votre code de vérification :"
            
            # Appel à l'API Resend
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
                    "to": [email],
                    "subject": subject,
                    "html": f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                        <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; padding: 20px;">
                            <h2 style="color: #667eea;">ParkimVoice Diagnosis Assistant</h2>
                            <p>Bonjour,</p>
                            <p>{message_intro}</p>
                            <div style="background: #f8f9fa; border: 2px dashed #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                                <h1 style="font-size: 48px; letter-spacing: 10px; color: #667eea; margin: 0;">{code}</h1>
                            </div>
                            <p>Ce code est valable pendant {settings.VERIFICATION_CODE_EXPIRE_MINUTES} minutes.</p>
                            <p>Si vous n'avez pas demandé cette action, ignorez simplement cet email.</p>
                        </div>
                    </body>
                    </html>
                    """
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Email envoyé à {email} (purpose: {purpose})")
                return True
            else:
                logger.error(f"❌ Erreur Resend : {response.text}")
                raise Exception(f"Erreur lors de l'envoi d'email: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi d'email: {str(e)}")
            raise Exception(f"Erreur lors de l'envoi d'email: {str(e)}")

    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Génère un code de vérification aléatoire"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def create_verification_code(db: Session, email: str, purpose: str = "registration") -> VerificationCode:
        """Crée un code de vérification et le stocke en base de données"""
        code = EmailService.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
        
        verification = VerificationCode(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        return verification

    @staticmethod
    def verify_code(db: Session, email: str, code: str, purpose: str = "registration") -> bool:
        """Vérifie si le code est valide"""
        verification = db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.purpose == purpose,
            VerificationCode.is_used == False,
            VerificationCode.expires_at > datetime.utcnow()
        ).order_by(VerificationCode.created_at.desc()).first()
        
        if verification:
            verification.is_used = True
            db.commit()
            return True
        return False

email_service = EmailService()