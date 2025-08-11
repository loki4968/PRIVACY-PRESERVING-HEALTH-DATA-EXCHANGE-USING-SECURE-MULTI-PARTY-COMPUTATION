import pyotp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

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
    
    return otp

def verify_otp(email: str, otp: str) -> bool:
    """Verify the OTP for the given email"""
    if email not in otp_store:
        return False
    
    stored_data = otp_store[email]
    stored_otp = stored_data['otp']
    timestamp = stored_data['timestamp']
    
    # Check if OTP is expired (5 minutes validity)
    if datetime.now() - timestamp > timedelta(minutes=5):
        del otp_store[email]
        return False
    
    # Increment attempts
    stored_data['attempts'] += 1
    
    # Check if too many attempts (max 3)
    if stored_data['attempts'] > 3:
        del otp_store[email]
        return False
    
    # Verify OTP
    if otp == stored_otp:
        del otp_store[email]  # Clear OTP after successful verification
        return True
    
    return False

def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP via email using smtplib"""
    try:
        # Get email configuration
        email_from = os.getenv('EMAIL_FROM')
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = os.getenv('SMTP_PORT')
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')

        # Validate email configuration
        if not all([email_from, smtp_host, smtp_port, smtp_user, smtp_password]):
            missing = []
            if not email_from: missing.append('EMAIL_FROM')
            if not smtp_host: missing.append('SMTP_HOST')
            if not smtp_port: missing.append('SMTP_PORT')
            if not smtp_user: missing.append('SMTP_USER')
            if not smtp_password: missing.append('SMTP_PASSWORD')
            raise ValueError(f"Missing email configuration: {', '.join(missing)}")

        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email
        msg['Subject'] = 'Your Health Data Exchange Verification Code'

        html = f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a56db;">Email Verification</h2>
            <p>Your verification code is:</p>
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

        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False 