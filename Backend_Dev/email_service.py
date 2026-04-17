"""
email_service.py — Email sending service for verification and notifications
Uses SMTP for sending emails. For production, use services like SendGrid, AWS SES, etc.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime


class EmailService:
    """
    Email service for sending verification and notification emails.
    
    Configuration via environment variables:
    - SMTP_HOST: SMTP server hostname
    - SMTP_PORT: SMTP server port
    - SMTP_USER: SMTP username
    - SMTP_PASSWORD: SMTP password
    - SMTP_FROM: Sender email address
    - SMTP_USE_TLS: Use TLS (true/false)
    - APP_URL: Application URL for verification links
    """
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "noreply@phishguard.ai")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.app_url = os.getenv("APP_URL", "http://localhost:5173")
        self.app_name = "PhishGuard AI"
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            print(f"⚠️  Email not configured. Would send to {to_email}: {subject}")
            print(f"   Content preview: {html_content[:200]}...")
            return True  # Return True in development mode
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connect and send
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_from, to_email, msg.as_string())
            server.quit()
            
            print(f"✅ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_email(self, email: str, username: str, verification_token: str) -> bool:
        """
        Send email verification email.
        
        Args:
            email: User's email address
            username: User's username
            verification_token: JWT token for email verification
        
        Returns:
            True if sent successfully
        """
        verification_link = f"{self.app_url}/verify-email?token={verification_token}"
        
        subject = f"Verify Your {self.app_name} Account"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #00d4ff; color: #000; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #00d4ff; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ {self.app_name}</h1>
                    <p>Welcome to Advanced Phishing Detection</p>
                </div>
                <div class="content">
                    <h2>Hello {username}!</h2>
                    <p>Thank you for creating an account with {self.app_name}. To get started, please verify your email address by clicking the button below:</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px; font-size: 12px;">{verification_link}</p>
                    
                    <p><strong>This link will expire in 24 hours.</strong></p>
                    
                    <p>If you didn't create this account, you can safely ignore this email.</p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    
                    <p>Stay safe online!</p>
                    <p><strong>The {self.app_name} Team</strong></p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} {self.app_name}. All rights reserved.</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_content)
    
    def send_welcome_email(self, email: str, username: str) -> bool:
        """
        Send welcome email after verification.
        
        Args:
            email: User's email address
            username: User's username
        
        Returns:
            True if sent successfully
        """
        subject = f"Welcome to {self.app_name}! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #00d4ff; color: #000; padding: 30px; text-align: center; border-radius: 10px; }}
                .content {{ padding: 30px 0; }}
                .feature {{ background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #00d4ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome {username}!</h1>
                    <p>Your account is now active</p>
                </div>
                <div class="content">
                    <h2>You're all set!</h2>
                    <p>Your email has been verified successfully. You can now enjoy all features of {self.app_name}:</p>
                    
                    <div class="feature">
                        <strong>🔍 URL Scanning</strong><br>
                        Analyze any URL for phishing threats in real-time
                    </div>
                    
                    <div class="feature">
                        <strong>📊 Scan History</strong><br>
                        Track and analyze all your previous scans
                    </div>
                    
                    <div class="feature">
                        <strong>🛡️ AI Protection</strong><br>
                        Powered by ensemble machine learning models
                    </div>
                    
                    <p>Start protecting yourself from phishing attacks today!</p>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{self.app_url}" style="background: #00d4ff; color: #000; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Start Scanning</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_content)
    
    def send_password_reset_email(self, email: str, username: str, reset_token: str) -> bool:
        """
        Send password reset email.
        
        Args:
            email: User's email address
            username: User's username
            reset_token: JWT token for password reset
        
        Returns:
            True if sent successfully
        """
        reset_link = f"{self.app_url}/reset-password?token={reset_token}"
        
        subject = f"Reset Your {self.app_name} Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ff6b6b; color: #fff; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #ff6b6b; color: #fff; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔑 Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hello {username},</h2>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>This link will expire in 1 hour.</p>
                    
                    <p><strong>If you didn't request this, please ignore this email or contact support if you have concerns.</strong></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_content)


# Global email service instance
email_service = EmailService()
