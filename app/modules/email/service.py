"""
Email service – production uses SES / Sendgrid.
For 50M users, need templating + queue + bounce handling.
"""
import structlog
from typing import Optional
from app.core.config import settings

logger = structlog.get_logger(__name__)

class EmailService:
    def __init__(self):
        self.enabled = settings.ENV == "production"

    async def send_verification(self, to: str, token: str):
        link = f"{settings.FRONTEND_URL}/verify?token={token}"
        subject = "Verify your VibeCodeTinder account"
        body = f"Welcome! Verify: {link}"
        logger.info("email_verification_sent", to=to, link=link)
        # In prod: await ses.send_email(...)
        return True

    async def send_match_email(self, to: str, other_name: str):
        subject = f"You matched with {other_name}! 🎉"
        body = f"It's a match! Say hi to {other_name}"
        logger.info("email_match_sent", to=to, other_name=other_name)
        return True

    async def send_password_reset(self, to: str, token: str):
        link = f"{settings.FRONTEND_URL}/reset?token={token}"
        logger.info("email_password_reset", to=to)
        return True

    async def send_security_alert(self, to: str, message: str):
        logger.info("email_security_alert", to=to, message=message)
        return True

email_service = EmailService()
