# coding: utf-8

import time
import hashlib
import hmac
import base64
import datetime


class KeySecret(object):
    def __init__(self, api_key, api_secret, api_passphrase):
        self.key = api_key
        self.secret = api_secret
        self.passphrase = api_passphrase


class Signature(object):
    def __init__(self, method: str, request_path: str, body: str, keysecret: KeySecret):
        """
        生成签名
        :param timestamp:
        :param method:
        :param request_path:
        """
        self.timestamp = datetime.datetime.utcnow().isoformat()[
                         :-3] + "Z" if request_path != "/users/self/verify" else f"{int(time.time())}"
        self.key = keysecret
        original_str = "".join([self.timestamp, method, request_path, body])
        self.signature = base64.b64encode(
            hmac.new(bytes(keysecret.secret, encoding='utf-8'), bytes(original_str, encoding='utf-8'),
                     digestmod=hashlib.sha256).digest())

    def headers(self):
        return {
            "OK-ACCESS-KEY": self.key.key,
            "OK-ACCESS-SIGN": str(self.signature, encoding='utf-8'),
            "OK-ACCESS-TIMESTAMP": self.timestamp,
            "OK-ACCESS-PASSPHRASE": self.key.passphrase,
            # "x-simulated-trading": "1"
        }
