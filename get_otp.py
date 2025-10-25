import sys
sys.path.append('backend')
from otp_utils import get_stored_otp

otp = get_stored_otp('test@example.com')
print(f"OTP for test@example.com: {otp}")
