import pyotp
import requests

from config import runtime_cfg


def verify_2fa(verification_code: str) -> bool:
    totp = pyotp.TOTP(runtime_cfg.general['2fa'])
    generated_code = totp.now()
    return verification_code == generated_code


# 创建day_pass，并通过bark发送到手机
def send_day_pass_to_phone(d_pass: str):
    bark_api = runtime_cfg.general['bark']
    url = bark_api + f'Hablar Admin Day Pass/{d_pass}'
    requests.post(url)
