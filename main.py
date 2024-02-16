import threading
import time
from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils import translate
from utils import tts
from utils import logging
import crud, models, schemas
from database import SessionLocal, engine
from config import runtime_cfg
from utils.auth import verify_2fa
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

app = FastAPI()
limiter = FastAPILimiter()


# print(pricing)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Admin
@app.post("/admin/topup/{key}", response_model=schemas.KeyLog)
async def get_key_info(key: str, body: schemas.KeyTopUp, db: Session = Depends(get_db)):
    db_key = crud.get_key_info(db, key=key)
    if db_key is None:
        raise HTTPException(status_code=404, detail="Key not found")
    if verify_2fa(body.verify_code):
        log = crud.update_key_balance(db, db_key.id, body)
        return log
    else:
        raise HTTPException(status_code=401, detail="Invalid 2FA")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    f = open('./html/admin.html', 'r')
    html = f.read()
    f.close()
    return html


@app.get("/lang/all", response_model=list[schemas.Lang])
async def get_langs(db: Session = Depends(get_db)):
    db_langs = crud.get_langs_all(db)
    print(db_langs)
    if db_langs is None:
        raise HTTPException(status_code=404, detail="No langs found")
    return db_langs


@app.get("/key/info/{key}", response_model=schemas.Key)
async def get_key_info(key: str, db: Session = Depends(get_db)):
    db_key = crud.get_key_info(db, key=key)
    if db_key is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return db_key


@app.get("/key/logs/{key}", response_model=list[schemas.KeyLog])
async def get_key_info(key: str, db: Session = Depends(get_db)):
    db_key = crud.get_key_info(db, key=key)
    if db_key is None:
        raise HTTPException(status_code=404, detail="Key not found")

    # 获取数据库模型
    db_logs = crud.get_key_logs_limit_20(db, db_key.id)

    # 将数据库模型转换为 Pydantic 模型
    logs = [schemas.KeyLog(
        key_id=log.key_id,
        trs_id=log.trs_id,
        change=log.change,
        success=log.success,
        ip=log.ip,
        device_operator=log.device_operator,
        fyi=log.fyi,
        timestamp=log.timestamp
    ) for log in db_logs]
    return logs


@app.post("/key/gen", response_model=schemas.Key)
async def gen_key(request: Request, db: Session = Depends(get_db)):
    ip = request.client.host
    ua = request.headers.get("User-Agent", '')
    db_key = crud.generate_key(db, ip, ua)
    if db_key is None:
        raise HTTPException(status_code=500, detail="Key gen error")
    return db_key


@app.get("/translate/logs/{key}", response_model=list[schemas.TrsLog])
async def get_key_info(key: str, db: Session = Depends(get_db)):
    db_key = crud.get_key_info(db, key=key)
    if db_key is None:
        raise HTTPException(status_code=404, detail="Key not found")

    # 获取数据库模型
    db_logs = crud.get_translate_logs_limit_20(db, db_key.id)

    # 将数据库模型转换为 Pydantic 模型
    logs = [schemas.TrsLog(
        key_id=log.key_id,
        source_language_code=log.source_language_code,
        target_language_code=log.target_language_code,
        source_text=log.source_text,
        result_text=log.result_text,
        timestamp=log.key_id,
    ) for log in db_logs]
    return logs


class TranslateQueryBody(BaseModel):
    source_language_code: str
    target_language_code: str
    source_text: str


class TranslateResponseBody(BaseModel):
    result_text: str
    result_lang_code: str
    audio_base64: str
    expense: int


from user_agents import parse


@app.post("/translate", response_model=TranslateResponseBody)
async def translate_request(request: Request, body: TranslateQueryBody, db: Session = Depends(get_db)):
    ip = request.client.host
    ua_str = request.headers.get("User-Agent", '')
    user_agent = parse(ua_str)
    ua = str(user_agent)
    key_str = request.headers.get("Key", '')
    if key_str is None:
        raise HTTPException(status_code=401, detail="empty key")

    key = crud.get_key_info(db, key_str)
    if key is None:
        raise HTTPException(status_code=401, detail="invalid key")
    if key.balance <= 0:
        key_log = schemas.KeyLog(
            key_id=key.id,
            trs_id=None,
            change=0,
            success=False,
            ip=ip,
            device_operator=ua[:128],
            fyi='点数不足',
            timestamp=logging.get_formatted_timestamp_str()
        )
        crud.add_key_log(db, key_log)
        raise HTTPException(status_code=401, detail="insufficient key balance")

    src_lang = crud.get_lang(db, body.source_language_code)
    if src_lang is None:
        raise HTTPException(status_code=404, detail="src_lang not found")

    tar_lang = crud.get_lang(db, body.target_language_code)
    if tar_lang is None:
        raise HTTPException(status_code=404, detail="tar_lang not found")

    source_text = body.source_text
    if len(source_text) > 2000:
        raise HTTPException(status_code=404, detail="Too much input")

    result = translate.translate(
        src_lang_code=src_lang.lang_code,
        tar_lang_code=tar_lang.lang_code,
        text=body.source_text
    )
    text_expense = int(max(result.tokens * float(runtime_cfg.pricing['text']['rate']), runtime_cfg['text']['minimum']))

    audio_file_path = tts.request_speech(key.id, tar_lang.voice_code, result.result_text)
    audio_base64 = tts.encode_audio_to_base64(audio_file_path)
    audio_expense = 0

    total_expense = text_expense + audio_expense
    # print(time.time())
    # 保存到数据库
    crud.update_key_balance(db, key.id, -total_expense)

    trs_log = schemas.TrsLog(
        key_id=key.id,
        source_language_code=src_lang.lang_code,
        target_language_code=tar_lang.lang_code,
        source_text=source_text,
        result_text=result.result_text,
        audio_file_path=audio_file_path,
        timestamp=logging.get_formatted_timestamp_str()
    )
    trs_id = crud.add_translate_log(db, trs_log)

    key_log = schemas.KeyLog(
        key_id=key.id,
        trs_id=trs_id,
        change=-total_expense,
        success=True,
        ip=ip,
        device_operator=ua[:128],
        fyi='正常计费',
        timestamp=logging.get_formatted_timestamp_str()
    )
    crud.add_key_log(db, key_log)

    response_body = TranslateResponseBody(
        result_text=result.result_text, result_lang_code=tar_lang.lang_code,
        audio_base64=audio_base64, expense=total_expense)
    # print(time.time()) 0.03s spent
    return response_body
