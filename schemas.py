from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# key表模型
class Key(BaseModel):
    key: str
    balance: int
    created_time: datetime
    last_balance_update_time: datetime

    class Config:
        orm_mode = True


class KeyTopUp(BaseModel):
    verify_code: str
    amount: int
    operator: str
    fyi: str

    class Config:
        orm_mode = True


# trs_log表模型
# 作为返回模型不应该出现 audio_file_path
class TrsLogBase(BaseModel):
    key_id: int
    source_language_code: str
    target_language_code: str
    source_text: str
    result_text: str
    timestamp: datetime

    class Config:
        orm_mode = True


class TrsLog(TrsLogBase):
    audio_file_path: Optional[str]

    class Config:
        orm_mode = True


# key_log表模型
class KeyLog(BaseModel):
    key_id: int
    trs_id: Optional[int]
    change: int
    success: bool
    ip: Optional[str]
    device_operator: Optional[str]
    fyi: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True


# lang

class Lang(BaseModel):
    id: int
    lang_code: str
    native_lang_name: str
    voice_code: str

    class Config:
        orm_mode = True
