# Email Configuration for OTP Functionality

## Overview

This document explains how to configure the email settings for the One-Time Password (OTP) functionality in the Health Data Exchange application. The application uses email to send verification codes during user registration and other sensitive operations.

**Current Status: Working ✅**

The email configuration has been tested and is working correctly. The OTP functionality is now operational.

## Configuration Steps

### 1. Backend Email Configuration

The email configuration is stored in the `backend/.env` file. The following environment variables need to be set:

```
EMAIL_FROM=your-email@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password
```

### 2. Gmail Configuration (Recommended)

If you're using Gmail as your email provider, follow these steps:

1. **Create a Gmail account** or use an existing one
2. **Enable 2-Step Verification**:
   - Go to your Google Account settings
   - Select Security
   - Under "Signing in to Google," select 2-Step Verification and follow the steps
3. **Generate an App Password**:
   - Go to your Google Account settings
   - Select Security
   - Under "Signing in to Google," select App passwords
   - Select the app (Other) and device you want to generate the app password for
   - Follow the instructions to generate the app password
   - Use this password in your `.env` file for the `SMTP_PASSWORD` variable

### 3. Testing Email Configuration

To test if your email configuration is working correctly, you can run the test script:

```bash
cd backend
python test_otp.py
```

This script will attempt to send a test email and verify the OTP functionality.

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check if your email and password are correct. For Gmail, ensure you're using an App Password, not your regular account password.

2. **Connection Refused**: Check if the SMTP server and port are correct. Some email providers might use different ports or require SSL/TLS.

3. **Rate Limiting**: Some email providers limit the number of emails you can send. Check if you've reached the limit.

### Development Mode

During development, if email sending is not configured or fails, the application will print the OTP to the console. Look for messages like:

```
📧 [DEV] Would send OTP 123456 to user@example.com
```

This allows testing the OTP functionality without actual email sending.

## Security Considerations

1. **Never commit your email credentials** to version control. The `.env` file should be included in `.gitignore`.

2. **Use environment variables** in production environments rather than `.env` files.

3. **Consider using a dedicated email service** like SendGrid, Mailgun, or Amazon SES for production environments.

## Additional Resources

- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [FastAPI Email Documentation](https://sabuhish.github.io/fastapi-mail/)
- [SMTP Protocol](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol)