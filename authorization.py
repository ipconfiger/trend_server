# coding: utf-8
import time
import uuid
import base64
import json

from sqlalchemy.ext.asyncio import AsyncSession

from database import DbWrapper, update
from forms import LoginForm, ChangePasswordForm
from json_persisted import JsonDatabase
from sqlalchemy_sugar import select, delete
from hashlib import sha256
from random import sample
from models import Account, Token
from secp256k1py import secp256k1

PRIVATE_KEY = '4e0f34016ef686e64dd7c3bbad138658abd94d52c65b438669f98c51149228e1'


def decrypt_password(enc_password, key, iv):
    try:
        return secp256k1.PrivateKey.restore(PRIVATE_KEY).decrypt(secp256k1.PublicKey.restore(key), enc_password, iv)
    except:
        return None


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


async def check_login(db: AsyncSession, form: LoginForm):
    account = await select(Account).where(Account.loginId == form.loginId).first(db)
    if account:
        raw_password = decrypt_password(form.password, form.key, form.iv)
        if verify_password(account.password, raw_password):
            token = Token(accountId=account.id, token=uuid.uuid4().hex, expire=int(time.time()) + 3600)
            db.add(token)
            await delete(Token).where(Token.expire < int(time.time())).execute(db)
            await update(Account).where(Account.loginId == form.loginId).values(valid=True).execute(db)
            return account, token
    return None, None


async def check_token(db: AsyncSession, token: str):
    credentialData = json.loads(base64.b64decode(token))
    enc_token = credentialData['p']
    random_pub = credentialData['k']
    iv = credentialData['i']
    token = decrypt_password(enc_token, random_pub, iv)
    token = await select(Token).where(Token.token == token).first(db)
    if token:
        return await db.get(Account, token.accountId)


async def account_list():
    async with DbWrapper() as db:
        for account in await select(Account).order_by(Account.loginId.desc()).scalars(db):
            print(f'{account.loginId}: {account.valid}')


async def change_password(db: AsyncSession, user: Account, form: ChangePasswordForm):
    raw_old = decrypt_password(form.oldPassword, form.oldKey, form.oldIv)
    raw_new = decrypt_password(form.newPassword, form.newKey, form.newIv)
    if verify_password(user.password, raw_old):
        user.password = gen_password(raw_new)
        return True
    else:
        return False


async def reset_password(user_name:str):
    async with DbWrapper() as db:
        for account in select(Account).where(Account.loginId == user_name).scalars(db):
            account.password = gen_password('123')
            await db.flush()
    print('Done!')


