import os
import jwt
from datetime import datetime, timedelta
from config import Settings

# Get settings
settings = Settings()

# Print the SECRET_KEY for debugging
print(f"SECRET_KEY: {settings.SECRET_KEY}")

# Create a test token
token_data = {
    "sub": "test@hospital.com",
    "role": "admin",
    "permissions": ["READ_PATIENT_DATA", "WRITE_PATIENT_DATA"],
    "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
    "type": "access"
}

# Encode the token
token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
print(f"\nGenerated token:\n{token}\n")

# Decode the token to verify
try:
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"Decoded token: {decoded}")
    print("Token is valid!")
except Exception as e:
    print(f"Error decoding token: {e}")