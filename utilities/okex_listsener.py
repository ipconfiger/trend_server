# coding=utf-8

import datetime
import time
import itertools
import json
import asyncio
import websockets
from configs import settings
from pydantic import BaseModel, Field

from utilities.data_dumper import get_holder
from .securety import Signature, KeySecret
from typing import List


class ExecInstruments(object):
    chn = "instruments"

    async def on_data(self, instId: str, data):
        for row in data:
            print(f"instId: {row['instId']}")


class ExecTickers(object):
    chn = 'tickers'

    async def on_data(self, inst_id: str, data: dict):
        holder = get_holder(inst_id, self.chn)
        for ticker in data:
            holder.append(ticker.get('instType'), inst_id, ticker.get('last'),
                          ticker.get('lastSz'),
                          ticker.get('askPx'),
                          ticker.get('askSz'), ticker.get('bidPx'), ticker.get('bidSz'),
                          ticker.get('open24h'),
                          ticker.get('high24h'),
                          ticker.get('low24h'), ticker.get('volCcy24h'), ticker.get('vol24h'),
                          ticker.get('sodUtc0'), ticker.get('sodUtc8'), ticker.get('ts'))


class ExecCandles(object):
    chn = 'candle1m'

    async def on_data(self, inst_id: str, data):
        holder = get_holder(inst_id, self.chn)
        for ts, open, high, low, close, vol, volCcy in data:
            holder.append('SPOT', ts, open, high, low, close, vol, volCcy)


class ChannelFilter(object):
    def __init__(self, triggers):
        self._triggers = triggers

    async def execute(self, data: dict):
        args = data.get('arg')
        print(f'args:{args} data:{data}')
        channel = args.get('channel')
        watched = [tg.chn for tg in self._triggers]
        # print(f"{channel} in {watched}")
        if channel in watched:
            for trigger in self._triggers:
                if channel == trigger.chn:
                    if data.get('data'):
                        instId = args.get('instId')
                        await trigger.on_data(instId, data.get('data'))
        else:
            print(f'unexpected chn:{channel}')


class Command(BaseModel):
    op: str = Field('', title="operation")
    args: List[dict] = Field({}, title="args")


class LoginArgs(BaseModel):
    apiKey: str = Field('', title="apiKey")
    passphrase: str = Field('', title="passphrase")
    timestamp: str = Field('', title="timestamp")
    sign: str = Field('', title="sign")


class SubscribeArgs(BaseModel):
    channel: str = Field('', title="channel")
    instId: str = Field('', title="product id")


async def private_main():
    api_key = "3d2a7e66-45dd-446d-89ab-1f3ec614733a"
    api_secret = "312D970B5F3B1F8E30550123BD2C5E0B"
    passphrase = 'nageRpyUpli1'
    uri = "wss://ws.okex.com:8443/ws/v5/private"
    async with websockets.connect(uri) as ws:
        securety = KeySecret(api_key, api_secret, passphrase)
        sign = Signature('GET', '/users/self/verify', '', securety)
        command = Command(op='login',
                          args=[LoginArgs(apiKey=api_key, passphrase=securety.passphrase, timestamp=sign.timestamp,
                                          sign=sign.signature).dict()])
        await ws.send(command.json())
        print(await ws.recv())


async def listen_private(on_change):
    uri = "wss://ws.okex.com:8443/ws/v5/private"
    async with websockets.connect(uri) as ws:
        securety = KeySecret(settings.API_KEY, settings.API_SECRET, settings.PASSPHRASE)
        sign = Signature('GET', '/users/self/verify', '', securety)
        command = Command(op='login',
                          args=[LoginArgs(apiKey=settings.API_KEY, passphrase=securety.passphrase,
                                          timestamp=sign.timestamp,
                                          sign=sign.signature).dict()])
        await ws.send(command.json())
        command2 = Command(op='subscribe', args=[{
            "channel": "balance_and_position"
        }])
        await ws.send(command2.json())
        while True:
            print(await ws.recv())


async def listen_public(subscribe_args: List[dict], filters: List[object]):
    uri = "wss://ws.okex.com:8443/ws/v5/public"
    async with websockets.connect(uri) as ws:
        try:
            command = Command(op='subscribe', args=subscribe_args)
            await ws.send(command.json())
            while True:
                event = await ws.recv()
                await ChannelFilter(filters).execute(json.loads(event))
                print('processed!')
        except KeyboardInterrupt:
            await ws.send(Command(op="unsubscribe", args=subscribe_args))


async def public_main():
    coins = ['FIL', 'ICP', 'LINK', 'XLM', 'CFX', 'FLOW', 'ZEC', 'LPT', 'SHIB']
    # products = ['BCD-BTC', 'ORS-USDT', 'TRIO-USDT']
    products = ['%s-USDT' % c for c in coins]
    channels = ['tickers', 'candle1m']
    await listen_public(list(itertools.chain(*[[{"channel": c, "instId": p} for c in channels] for p in products])),
                        [ExecTickers(), ExecCandles()])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen_public([{
      "channel": "tickets",
      "instType": "XRP-USDC"
    },
    {
        "channel": "tickets",
        "instType": "DASH-USDT"
    },
    {
        "channel": "tickets",
        "instType": "DIA-USDT"
    }
    ], [ExecInstruments(), ExecCandles()]))
