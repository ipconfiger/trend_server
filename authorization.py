# coding: utf-8
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from database import DbWrapper, update
from json_persisted import JsonDatabase
from sqlalchemy_sugar import select, delete
from hashlib import sha256
from random import sample
from models import Account, Token


def gen_password(password: str):
    salt = ''.join(sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', 4))
    hash_pass = sha256(f'{salt}-{password}'.encode()).hexdigest()
    return f'{salt}/{hash_pass}'


def verify_password(origin_password: str, password: str):
    salt, hash_pass = origin_password.split('/')
    check_hash = sha256(f'{salt}-{password}'.encode()).hexdigest()
    return check_hash == hash_pass


async def create_account(loginId: str, password: str):
    async with DbWrapper() as db:
        db.add(Account(loginId=loginId, password=gen_password(password), valid=True))
        await db.flush()


async def check_login(db: AsyncSession, loginId: str, password: str):
    print(f"u:{loginId} p:{password}")
    account = await select(Account).where(Account.loginId == loginId).first(db)
    if account:
        if verify_password(account.password, password):
            token = Token(accountId=account.id, token=uuid.uuid4().hex, expire=int(time.time()) + 3600)
            db.add(token)
            await delete(Token).where(Token.expire < int(time.time())).execute(db)
            await update(Account).where(Account.loginId == loginId).values(valid=True).execute(db)
            return account, token
    return None, None


async def check_token(db: AsyncSession, token: str):
    token = await select(Token).where(Token.token == token).first(db)
    if token:
        return await db.get(Account, token.accountId)


async def account_list():
    async with DbWrapper() as db:
        for account in await select(Account).order_by(Account.loginId.desc()).scalars(db):
            print(f'{account.loginId}: {account.valid}')


def delete_account(loginId: str):
    with JsonDatabase('login') as db:
        db.rem(loginId, Account)



