import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncResult
from sqlalchemy.orm import sessionmaker
from functools import wraps
from config import DB_URI, DB_URI2
from sqlalchemy.sql.dml import Update
from sqlalchemy.util.langhelpers import public_factory

engine = create_async_engine(DB_URI)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=True)


class AsyncUpdate(Update):
    async def execute(self, session: AsyncSession) -> AsyncResult:
        return await session.execute(self)


update = public_factory(AsyncUpdate, ".sql.expression.update")


async def get_session() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with Session() as session:
        yield session
        await session.flush()
        await session.commit()


class DbWrapper(object):
    async def __aenter__(self):
        self.db: AsyncSession = Session()
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            await self.db.rollback()
            logging.error(f'<{exc_type}>{exc_val}:{exc_tb}')
        else:
            await self.db.commit()
        await self.db.close()


class SyncDbWrapper(object):
    sync_engin = create_engine(DB_URI2)
    SyncSession = sessionmaker(bind=sync_engin, expire_on_commit=False, autocommit=False, autoflush=True)

    def __enter__(self):
        self.db = SyncDbWrapper.SyncSession()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.db.rollback()
            logging.error(f'<{exc_type}>{exc_val}:{exc_tb}')
        else:
            self.db.commit()
        self.db.close()


class SessionWrapper(object):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    def query(self, *cls):
        self.db_session.query(*cls)

    def add(self, *rows):
        for row in rows:
            self.db_session.insert(row)

    def delete(self, *rows):
        for row in rows:
            self.db_session.delete(row)


def tx_wrapper(func):
    @wraps(func)
    def processor(*args, **kwargv):
        base_service = args[0]
        try:
            response = func(*args, **kwargv)
            base_service.commit()
            return response
        except Exception as ex:
            logging.error('DB Error:%s', ex)
            base_service.rollback()
            raise ex

    return processor
