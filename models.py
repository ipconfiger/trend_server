# coding=utf-8

import sqlalchemy
import uuid
from sqlalchemy.dialects.postgresql import UUID

metadata = sqlalchemy.MetaData()

tickers = sqlalchemy.Table(
    "tickers",
    metadata,
    sqlalchemy.Column("id", UUID, primary_key=True, default=uuid.uuid1),
    sqlalchemy.Column("src", sqlalchemy.SmallInteger),
    sqlalchemy.Column("instType", sqlalchemy.String(16)),
    sqlalchemy.Column("instId", sqlalchemy.String(32)),
    sqlalchemy.Column("last", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("lastSz", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("askPx", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("askSz", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("bidPx", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("bidSz", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("open24h", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("high24h", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("low24h", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("volCcy24h", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("vol24h", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("sodUtc0", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("sodUtc8", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("ts", sqlalchemy.BigInteger),
)


candles = sqlalchemy.Table(
    "candles",
    metadata,
    sqlalchemy.Column("id", UUID, primary_key=True, default=uuid.uuid1),
    sqlalchemy.Column("src", sqlalchemy.SmallInteger),
    sqlalchemy.Column("instType", sqlalchemy.String(16)),
    sqlalchemy.Column("instId", sqlalchemy.String(32)),
    sqlalchemy.Column("ts", sqlalchemy.BigInteger),
    sqlalchemy.Column("open", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("high", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("low", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("close", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("vol", sqlalchemy.Numeric(36, 18)),
    sqlalchemy.Column("volCcy", sqlalchemy.Numeric(36, 18)),
)


