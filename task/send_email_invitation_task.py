from app.services.email_service import email_service
from datetime import datetime
from celery_worker import celery_app
import dotenv
dotenv.load_dotenv()

@celery_app.task(name="send_team_invitation_email")
def send_team_invitation_email(to_email: str, inviter_name: str, company_name: str, invitation_id: str, expires_at: datetime):
    """
    Send team invitation email asynchronously.
    """
    try:
        success = email_service.send_team_invitation(
            to_email=to_email,
            inviter_name=inviter_name,
            company_name=company_name,
            invitation_id=invitation_id,
            expires_at=expires_at
        )
        return {"status": "success", "message": "Email sent successfully"} if success else {"status": "failed", "message": "Email sending failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}