# coding=utf-8
from sqlalchemy import Column, String, Integer, Index, Text, Boolean, BigInteger, Numeric, SmallInteger
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.dialects.postgresql import UUID

import uuid
import time


class ModelBase:
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    # 创建时间
    create_ts = Column(BigInteger, index=True, default=time.time, nullable=False)
    # 更新时间
    update_ts = Column(BigInteger, index=True, default=time.time, nullable=False)


# 创建对象的基类:
Base = declarative_base(cls=ModelBase)


class Account(Base):
    loginId = Column(String(32), unique=True, nullable=False)
    password = Column(String(70), nullable=False)
    valid = Column(Boolean)


class Token(Base):
    accountId = Column(UUID(as_uuid=True), index=True, nullable=False)
    token = Column(String(32), unique=True, nullable=False)
    expire = Column(Integer, nullable=False, server_default='0')


class ExecutionTask(Base):
    accountId = Column(UUID(as_uuid=True), index=True, nullable=False)
    product = Column(String(36), nullable=False)
    startDate = Column(String(10), nullable=False)
    endDate = Column(String(10), nullable=False)
    # increment = Column(SmallInteger, nullable=False)
    # windowSize = Column(SmallInteger, nullable=False)
    # windowUnit = Column(String(1), nullable=False)
    taskType = Column(SmallInteger, nullable=False, server_default='0')
    processing = Column(Boolean, nullable=False, server_default='0')
    percentage = Column(SmallInteger, nullable=False, server_default='0')
    resultId = Column(UUID(as_uuid=True), nullable=True)
    params = Column(Text)


class SavedTask(Base):
    accountId = Column(UUID(as_uuid=True), index=True, nullable=False)
    product = Column(String(36), nullable=False)
    startDate = Column(String(10), nullable=False)
    endDate = Column(String(10), nullable=False)
    taskType = Column(SmallInteger, nullable=False, server_default='0')
    processing = Column(Boolean, nullable=False, server_default='0')
    percentage = Column(SmallInteger, nullable=False, server_default='0')
    resultId = Column(UUID(as_uuid=True), nullable=True)
    params = Column(Text)


class KeptTask(Base):
    accountId = Column(UUID(as_uuid=True), index=True, nullable=False)
    product = Column(String(36), nullable=False)
    startDate = Column(String(10), nullable=False)
    endDate = Column(String(10), nullable=False)
    taskType = Column(SmallInteger, nullable=False, server_default='0')
    processing = Column(Boolean, nullable=False, server_default='0')
    percentage = Column(SmallInteger, nullable=False, server_default='0')
    resultId = Column(UUID(as_uuid=True), nullable=True)
    params = Column(Text)


class ExecutionResult(Base):
    accountId = Column(UUID(as_uuid=True), index=True, nullable=False)
    taskId = Column(UUID(as_uuid=True), index=True, nullable=False)
    windowCount = Column(SmallInteger, nullable=False, server_default='0')
    successCount = Column(SmallInteger, nullable=False, server_default='0')
    eslapshed = Column(Integer, nullable=False, server_default='0')


class DataWindow(Base):
    accountId = Column(UUID(as_uuid=True), index=True, nullable=False)
    taskId = Column(UUID(as_uuid=True), index=True, nullable=False)
    resultId = Column(UUID(as_uuid=True), index=True, nullable=True)
    date = Column(String(10), nullable=False, server_default='')
    file_path = Column(String(100), nullable=False, server_default='')
    startIdx = Column(Integer, nullable=False, server_default='0')
    startTs = Column(BigInteger, nullable=False, server_default='0')
    startVal = Column(Numeric(26, 18), nullable=False, server_default='0.0')
    firstIdx = Column(Integer, nullable=False, server_default='0')
    firstVal = Column(Numeric(26, 18), nullable=False, server_default='0.0')
    firstTs = Column(BigInteger, nullable=False, server_default='0')
    highestIdx = Column(Integer, nullable=False, server_default='0')
    highestVal = Column(Numeric(26, 18), nullable=False, server_default='0.0')
    highestTs = Column(BigInteger, nullable=False, server_default='0')
    lastIdx = Column(Integer, nullable=False, server_default='0')
    lastVal = Column(Numeric(26, 18), nullable=False, server_default='0.0')
    lastTs = Column(BigInteger, nullable=False, server_default='0')


class ShareRequest(Base):
    accountId = Column(UUID(as_uuid=True), index=True, nullable=False)
    taskId = Column(UUID(as_uuid=True), index=True, nullable=False)
    resultId = Column(UUID(as_uuid=True), index=True, nullable=True)
    code = Column(String(6), unique=True)





