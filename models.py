from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Key(Base):
    __tablename__ = 'key'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(32), nullable=False)
    balance = Column(Integer, nullable=False)
    created_time = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", nullable=False)
    last_balance_update_time = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", nullable=False)


class TrsLog(Base):
    __tablename__ = 'trs_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key_id = Column(Integer, ForeignKey('key.id'))
    source_language_code = Column(String(5), nullable=False)
    target_language_code = Column(String(5), nullable=False)
    source_text = Column(Text, nullable=False)
    result_text = Column(Text, nullable=False)
    audio_file_path = Column(String(512))
    timestamp = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", nullable=False)
    key = relationship('Key')


class KeyLog(Base):
    __tablename__ = 'key_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key_id = Column(Integer, ForeignKey('key.id'))
    trs_id = Column(Integer, ForeignKey('trs_log.id'))
    change = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    ip = Column(String(45))
    device_operator = Column(String(128))
    fyi = Column(String(32))
    timestamp = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP", nullable=False)
    key = relationship('Key')
    trs_log = relationship('TrsLog')


class Lang(Base):
    __tablename__ = 'lang'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lang_code = Column(String(8), nullable=False)
    native_lang_name = Column(String(128), nullable=False)
    voice_code = Column(String(32), nullable=False)


class AdminPass(Base):
    __tablename__ = 'admin_pass'
    id = Column(Integer, primary_key=True, autoincrement=True)
    d_pass = Column(String(32), nullable=False)
    expire_time = Column(TIMESTAMP, nullable=False)