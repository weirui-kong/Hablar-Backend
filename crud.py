import datetime
import hashlib

from sqlalchemy.orm import Session
from sqlalchemy import desc
import random
import time

import main
import models, schemas
import utils.logging
from database import SessionLocal


# admin创建 daypass，有效期默认一天
# create table admin_pass
# (
#     id          int auto_increment,
#     d_pass        char(32) not null,
#     expire_time datetime not null
# );
def create_day_pass(db: Session) -> str:
    # 生成一个随机的字符串
    d_pass = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))
    # 有效期默认一天
    expire_time = datetime.datetime.now() + datetime.timedelta(days=1)
    db_pass = models.AdminPass(
        d_pass=d_pass,
        expire_time=expire_time
    )
    db.add(db_pass)
    db.commit()
    db.refresh(db_pass)
    return d_pass


def auth_day_pass(db: Session, d_pass: str) -> bool:
    db_pass = db.query(models.AdminPass).filter(models.AdminPass.d_pass == d_pass).first()
    if db_pass is None:
        return False
    if db_pass.expire_time < datetime.datetime.now():
        return False
    return True


def get_langs_all(db: Session) -> [models.Lang]:
    db_langs = db.query(models.Lang).all()
    return db_langs


def get_lang(db: Session, lang_code: str) -> models.Lang:
    db_lang = db.query(models.Lang).filter(models.Lang.lang_code == lang_code).first()
    return db_lang


def generate_key(db: Session, ip: str, ua: str):
    # 生成一个随机的字符串作为盐
    salt = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    # 获取当前时间戳
    current_time = str(int(time.time()))
    # 将所有信息拼接起来
    data_to_hash = f"{salt}{current_time}{ip}{ua}"
    # 生成md5
    md5_object = hashlib.md5(data_to_hash.encode())
    md5_data = md5_object.hexdigest()

    db_key = models.Key(
        key=md5_data,
        balance=0,
        created_time=datetime.datetime.now(),
        last_balance_update_time=datetime.datetime.now()
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


def get_key_info(db: Session, key: str) -> models.Key:
    return db.query(models.Key).filter(models.Key.key == key).first()


def get_all_keys(db: Session) -> [models.Key]:
    return db.query(models.Key).all()


def update_key_balance(db: Session, key_id: int, amount: int):
    key_record = db.query(models.Key).filter_by(id=key_id).first()

    # 计算新的余额
    new_balance = key_record.balance + amount

    # 更新 key 表中的余额和最后更新时间
    key_record.balance = new_balance
    key_record.last_balance_update_time = utils.logging.get_formatted_timestamp_str()

    # 提交更改x
    db.commit()

    # # 新增key_log记录
    #
    # log = models.KeyLog(
    #     key_id=key_record.id,
    #     change=data.amount,
    #     success=True,
    #     device_operator=data.operator,
    #     fyi=data.fyi,
    #     timestamp=utils.logging.get_formatted_timestamp_str()
    # )
    #
    # db.add(log)
    # db.commit()
    #
    # db.refresh(log)
    # return log


def add_translate_log(db: Session, trs_log: schemas.TrsLog) -> int:
    db_log = models.TrsLog(
        key_id=trs_log.key_id,
        source_language_code=trs_log.source_language_code,
        target_language_code=trs_log.target_language_code,
        source_text=trs_log.source_text,
        result_text=trs_log.result_text,
        audio_file_path=trs_log.audio_file_path,
        timestamp=trs_log.timestamp
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log.id


def get_translate_logs_limit_20(db: Session, key_id: int) -> [models.TrsLog]:
    return db.query(models.TrsLog).filter(models.TrsLog.key_id == key_id).order_by(desc(models.TrsLog.id)).limit(
        20).all()


def add_key_log(db: Session, key_log: schemas.KeyLog) -> models.KeyLog:
    db_log = models.KeyLog(
        key_id=key_log.key_id,
        trs_id=key_log.trs_id,
        change=key_log.change,
        success=key_log.success,
        ip=key_log.ip,
        device_operator=key_log.device_operator,
        fyi=key_log.fyi,
        timestamp=key_log.timestamp
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_key_logs_limit_20(db: Session, key_id: int) -> [models.KeyLog]:
    return db.query(models.KeyLog).filter(models.KeyLog.key_id == key_id).order_by(desc(models.KeyLog.id)).limit(
        20).all()
