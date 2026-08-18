"""Notification-related background tasks."""
from app.tasks.celery_app import celery_app
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_sms_otp(self, mobile_number: str, otp_code: str):
    """Send OTP via SMS using Twilio."""
    try:
        from twilio.rest import Client
        
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio not configured, OTP not sent")
            return {
                "status": "skipped",
                "message": "Twilio not configured",
                "otp": otp_code if settings.DEBUG else None
            }
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=f"Your Smart Agriculture verification code is: {otp_code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=mobile_number
        )
        
        logger.info(f"OTP sent to {mobile_number}, SID: {message.sid}")
        
        return {
            "status": "success",
            "message_sid": message.sid
        }
        
    except Exception as exc:
        logger.error(f"Error sending SMS: {exc}")
        self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, max_retries=3)
def send_verification_email(self, user_id: int, email: str, token: str):
    """Send email verification link."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP not configured, email not sent")
            return {"status": "skipped", "message": "SMTP not configured"}
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Verify your Smart Agriculture account"
        msg["From"] = settings.SMTP_USER
        msg["To"] = email
        
        verification_url = f"https://smart-agricultural-assistance-system-1.onrender.com/api/v1/auth/verify-email?token={token}"
        
        html = f"""
        <html>
        <body>
            <h2>Welcome to Smart Agriculture Platform</h2>
            <p>Please click the link below to verify your email address:</p>
            <a href="{verification_url}">Verify Email</a>
            <p>If you didn't create an account, please ignore this email.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())
        
        logger.info(f"Verification email sent to {email}")
        
        return {"status": "success", "email": email}
        
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        self.retry(exc=exc, countdown=30)


@celery_app.task
def send_weather_alert_notification(user_id: int, alert_data: dict):
    """Send weather alert notification to user."""
    logger.info(f"Sending weather alert to user {user_id}")
    
    # Implementation would send push notification, SMS, or email
    # based on user preferences
    
    return {"status": "success", "user_id": user_id}


@celery_app.task
def send_price_alert_notification(user_id: int, crop: str, price: float):
    """Send price alert notification to user."""
    logger.info(f"Sending price alert to user {user_id} for {crop}")
    
    return {"status": "success", "user_id": user_id, "crop": crop}
