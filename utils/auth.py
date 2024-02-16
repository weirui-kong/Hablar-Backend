import pyotp
from config import runtime_cfg


def verify_2fa(verification_code) -> bool:
    totp = pyotp.TOTP(runtime_cfg.general['2fa'])
    generated_code = totp.now()
    return verification_code == generated_code
