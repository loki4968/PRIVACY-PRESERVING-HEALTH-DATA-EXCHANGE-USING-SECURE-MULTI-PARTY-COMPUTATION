import pyotp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OTP storage (in production, use Redis or a database)
otp_store: Dict[str, Dict] = {}

def generate_otp(email: str) -> str:
    """Generate a 6-digit OTP and store it with timestamp"""
    # Generate a 6-digit OTP
    totp = pyotp.TOTP(pyotp.random_base32(), digits=6, interval=300)  # 5 minutes validity
    otp = totp.now()
    
    # Store OTP with timestamp
    otp_store[email] = {
        'otp': otp,
        'timestamp': datetime.now(),
        'attempts': 0
    }
    
    # Log OTP for development (remove in production)
    logger.info(f"🔐 Generated OTP for {email}: {otp}")
    print(f"🔐 [DEV] OTP for {email}: {otp}")
    
    return otp

def verify_otp(email: str, otp: str) -> bool:
    """Verify the OTP for the given email"""
    if email not in otp_store:
        logger.warning(f"❌ No OTP found for email: {email}")
        return False
    
    stored_data = otp_store[email]
    stored_otp = stored_data['otp']
    timestamp = stored_data['timestamp']
    
    # Check if OTP is expired (5 minutes validity)
    if datetime.now() - timestamp > timedelta(minutes=5):
        logger.warning(f"❌ OTP expired for email: {email}")
        del otp_store[email]
        return False
    
    # Increment attempts
    stored_data['attempts'] += 1
    
    # Check if too many attempts (max 3)
    if stored_data['attempts'] > 3:
        logger.warning(f"❌ Too many attempts for email: {email}")
        del otp_store[email]
        return False
    
    # Verify OTP
    if otp == stored_otp:
        logger.info(f"✅ OTP verified successfully for email: {email}")
        del otp_store[email]  # Clear OTP after successful verification
        return True
    
    logger.warning(f"❌ Invalid OTP for email: {email}")
    return False

def send_otp_email(email: str, otp: str, purpose: str = "email_verification") -> bool:
    """Send OTP via email using smtplib
    
    Args:
        email: The recipient email address
        otp: The one-time password to send
        purpose: The purpose of the OTP (email_verification or password_reset)
    """
    try:
        # Get email configuration
        email_from = os.getenv('EMAIL_FROM') or os.getenv('SMTP_USERNAME')
        smtp_host = os.getenv('SMTP_HOST') or os.getenv('SMTP_SERVER')
        smtp_port = os.getenv('SMTP_PORT')
        smtp_user = os.getenv('SMTP_USER') or os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')

        # Check if email configuration is available
        if not all([email_from, smtp_host, smtp_port, smtp_user, smtp_password]):
            missing = []
            if not email_from: missing.append('EMAIL_FROM/SMTP_USERNAME')
            if not smtp_host: missing.append('SMTP_HOST/SMTP_SERVER')
            if not smtp_port: missing.append('SMTP_PORT')
            if not smtp_user: missing.append('SMTP_USER/SMTP_USERNAME')
            if not smtp_password: missing.append('SMTP_PASSWORD')
            
            logger.warning(f"⚠️  Missing email configuration: {', '.join(missing)}")
            logger.info(f"📧 [DEV] Would send OTP {otp} to {email} for {purpose}")
            print(f"📧 [DEV] Would send OTP {otp} to {email} for {purpose}")
            print("💡 Configure SMTP settings in .env file for real email sending")
            return True  # Return True for development

        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email
        
        # Set subject and content based on purpose
        if purpose == "password_reset":
            msg['Subject'] = 'Your Health Data Exchange Password Reset Code'
            title = "Password Reset"
            description = "Use this code to reset your password:"
        else:  # Default to email verification
            msg['Subject'] = 'Your Health Data Exchange Verification Code'
            title = "Email Verification"
            description = "Your verification code is:"

        html = f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a56db;">{title}</h2>
            <p>{description}</p>
            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; letter-spacing: 4px;">{otp}</span>
            </div>
            <p>This code will expire in 5 minutes.</p>
            <p style="color: #6b7280; font-size: 14px;">
                If you didn't request this code, please ignore this email.
            </p>
        </div>
        '''

        msg.attach(MIMEText(html, 'html'))

        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"✅ OTP email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send OTP email to {email}: {str(e)}")
        print(f"📧 [DEV] Failed to send email, but OTP is: {otp}")
        return False

def get_stored_otp(email: str) -> str:
    """Get stored OTP for development/testing purposes"""
    if email in otp_store:
        return otp_store[email]['otp']
    return None 

def send_email(email: str, subject: str, body: str) -> bool:
    """Send email using smtplib"""
    try:
        # Get email configuration
        email_from = os.getenv('EMAIL_FROM') or os.getenv('SMTP_USERNAME')
        smtp_host = os.getenv('SMTP_HOST') or os.getenv('SMTP_SERVER')
        smtp_port = os.getenv('SMTP_PORT')
        smtp_user = os.getenv('SMTP_USER') or os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')

        # Check if email configuration is available
        if not all([email_from, smtp_host, smtp_port, smtp_user, smtp_password]):
            missing = []
            if not email_from: missing.append('EMAIL_FROM/SMTP_USERNAME')
            if not smtp_host: missing.append('SMTP_HOST/SMTP_SERVER')
            if not smtp_port: missing.append('SMTP_PORT')
            if not smtp_user: missing.append('SMTP_USER/SMTP_USERNAME')
            if not smtp_password: missing.append('SMTP_PASSWORD')
            
            logger.warning(f"⚠️  Missing email configuration: {', '.join(missing)}")
            logger.info(f"📧 [DEV] Would send email to {email} with subject: {subject}")
            print(f"📧 [DEV] Would send email to {email} with subject: {subject}")
            print("💡 Configure SMTP settings in .env file for real email sending")
            return True  # Return True for development

        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"✅ Email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {email}: {str(e)}")
        print(f"📧 [DEV] Failed to send email to {email}, error: {str(e)}")
        return False