import os
from typing import Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    """
    Email service for sending team invitations.
    
    Supports SMTP email sending with configurable templates.
    """
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.app_base_url = settings.APP_BASE_URL
    
    def send_team_invitation(
        self,
        to_email: str,
        inviter_name: str,
        company_name: str,
        invitation_id: str,
        expires_at: datetime
    ) -> bool:
        """
        Send team invitation email.
        
        Args:
            to_email: Recipient email address
            inviter_name: Name of person sending invitation
            company_name: Company name
            invitation_id: Unique invitation ID
            expires_at: When invitation expires
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create invitation URL
            invitation_url = f"{self.app_base_url}/invitations/accept/{invitation_id}"
            
            # Format expiration date
            expiry_date = expires_at.strftime("%B %d, %Y")
            
            # Email subject
            subject = f"Join {company_name} on CareerConnect"
            
            # Email body (HTML template)
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Team Invitation</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4f46e5; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9fafb; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #4f46e5; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Team Invitation</h1>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p><strong>{inviter_name}</strong> has invited you to join <strong>{company_name}</strong> on CareerConnect.</p>
                        <p>CareerConnect helps teams collaborate on recruitment, manage job postings, and streamline the hiring process.</p>
                        
                        <p style="text-align: center;">
                            <a href="{invitation_url}" class="button">Accept Invitation</a>
                        </p>
                        
                        <p>This invitation will expire on <strong>{expiry_date}</strong>.</p>
                        
                        <p>If you don't have an account yet, you'll be able to create one when you click the link above.</p>
                        
                        <p>Best regards,<br>
                        The CareerConnect Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(to_email, subject, body)
            
        except Exception as e:
            # Log error instead of printing in production
            return False
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email using SMTP.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (HTML)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"SMTP error: {e}")
            return False
    
    def send_invitation_reminder(
        self,
        to_email: str,
        company_name: str,
        invitation_id: str,
        expires_at: datetime
    ) -> bool:
        """
        Send reminder email for pending invitation.
        
        Args:
            to_email: Recipient email
            company_name: Company name
            invitation_id: Invitation ID
            expires_at: Expiration date
            
        Returns:
            True if successful, False otherwise
        """
        try:
            invitation_url = f"{self.app_base_url}/invitations/accept/{invitation_id}"
            expiry_date = expires_at.strftime("%B %d, %Y")
            
            subject = f"Reminder: Join {company_name} on CareerConnect"
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Invitation Reminder</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #f59e0b; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9fafb; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #f59e0b; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Invitation Reminder</h1>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p>This is a friendly reminder that you have a pending invitation to join <strong>{company_name}</strong> on CareerConnect.</p>
                        
                        <p style="text-align: center;">
                            <a href="{invitation_url}" class="button">Accept Invitation</a>
                        </p>
                        
                        <p>This invitation will expire on <strong>{expiry_date}</strong>.</p>
                        
                        <p>Best regards,<br>
                        The CareerConnect Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(to_email, subject, body)
            
        except Exception as e:
            # Log email failure
            return False


# Global email service instance
email_service = EmailService()
