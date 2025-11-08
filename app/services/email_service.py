import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging

from app.core.config import settings
from app.core.logging import log_operation

logger = logging.getLogger("email_services")


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
    
    @log_operation(logger)
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """Send email via Gmail SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Attach body
            mime_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, mime_type, "utf-8"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @log_operation(logger)
    async def send_otp_email(self, to_email: str, otp_code: str, otp_type: str) -> bool:
        """Send OTP email"""
        if otp_type == "register":
            subject = "Verification Code for Registration"
            purpose = "completing registration"
        else:  # reset_password
            subject = "Verification Code for Reset Password"
            purpose = "resetting password"

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; }}
                .otp-code {{ 
                    font-size: 32px; 
                    font-weight: bold; 
                    color: #4CAF50; 
                    text-align: center; 
                    padding: 20px;
                    background-color: #fff;
                    border: 2px dashed #4CAF50;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .warning {{ color: #f44336; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{settings.SMTP_FROM_NAME}</h1>
                </div>
                <div class="content">
                    <h2>OTP Verification Code</h2>
                    <p>You are receiving this email because there was a request to {purpose} your account.</p>
                    <p>Please use the following OTP code:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p><span class="warning">This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.</span></p>
                    <p>If you did not make this request, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>This email was sent automatically, please do not reply to this email.</p>
                    <p>&copy; 2024 {settings.SMTP_FROM_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body, is_html=True)
    
    @log_operation(logger)
    async def send_welcome_email(self, to_email: str, full_name: str, generated_password: str) -> bool:
        """Send welcome email with generated password"""
        subject = "Welcome to Our Service!"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; }}
                .password-box {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #4CAF50; 
                    text-align: center; 
                    padding: 15px;
                    background-color: #fff;
                    border: 2px dashed #4CAF50;
                    margin: 20px 0;
                    letter-spacing: 3px;
                }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{settings.SMTP_FROM_NAME}</h1>
                </div>
                <div class="content">
                    <h2>Welcome, {full_name}!</h2>
                    <p>Your account has been successfully created. Below is your generated password:</p>
                    <div class="password-box">{generated_password}</div>
                    <p>Please log in using this password and change it after your first login for security reasons.</p>
                    <p>We are excited to have you on board!</p>
                </div>
                <div class="footer">
                    <p>This email was sent automatically, please do not reply to this email.</p>
                    <p>&copy; 2024 {settings.SMTP_FROM_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body, is_html=True)
    
    @log_operation(logger)
    async def send_reset_password_email(to_email: str, otp_code: str) -> bool:
        """
        Send password reset email with OTP link
        
        Args:
            to_email: User email address
            otp_code: OTP code for password reset
            
        Returns:
            bool: True if email sent successfully
        """
        reset_link = f"{settings.FRONTEND_URL}{settings.FRONTEND_RESET_PASSWORD_ENDPOINT}?otp={otp_code}"
        
        subject = "Reset Your Password"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">Password Reset Request</h2>
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Click the button below to reset it:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="background-color: #4CAF50; 
                                  color: white; 
                                  padding: 12px 30px; 
                                  text-decoration: none; 
                                  border-radius: 5px;
                                  display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                        {reset_link}
                    </p>
                    <p style="color: #666; font-size: 14px;">
                        This link will expire in 15 minutes for security reasons.
                    </p>
                    <p style="color: #666; font-size: 14px;">
                        If you didn't request this password reset, please ignore this email.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        © {settings.EMAIL_FROM_NAME}. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return await EmailService.send_email(to_email, subject, body)
    
    @log_operation(logger)
    async def send_email_change_notification(self, to_email: str, full_name: str) -> bool:
        """Send email change notification"""
        subject = "Email Address Changed"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{settings.SMTP_FROM_NAME}</h1>
                </div>
                <div class="content">
                    <h2>Email Address Changed</h2>
                    <p>Dear {full_name},</p>
                    <p>This is to notify you that your account's email address has been successfully changed.</p>
                    <p>If you did not authorize this change, please contact our support team immediately.</p>
                </div>
                <div class="footer">
                    <p>© {settings.SMTP_FROM_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return await EmailService.send_email(to_email, subject, body)