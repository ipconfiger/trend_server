# coding=utf-8

import requests
from pydantic import BaseModel, Field
from typing import List, Optional


class CoinInfo(BaseModel):
    coincode: str = Field('', title="coincode")
    coinsymbol: str = Field('', title="coinsymbol")
    nativename: str = Field('', title="nativename")
    rate: str = Field('', title="rate")
    tagcode: str = Field('', title="tagcode")
    tagname: str = Field('', title="tagname")


class GrayItem(BaseModel):
    time: int
    coinsymbol: str
    contractamount: float
    contractvalue: float
    price: float
    secprice: Optional[float]
    rate: Optional[float]
    change_24h: float
    change_week: float
    change_30day: float
    lastvalue_30day: float
    coincode: str
    grayname: str
    lastcost: float


class Data(BaseModel):
    list: List[GrayItem]
    trend: List
    total: float
    rate: float
    ratetime: int


def json_from_page(url):
    r = requests.get(url)
    return r.json()


def rise_coins():
    for json_dict in json_from_page('https://dncapi.bqrank.net/api/concept/coinrisefall?type=1&pagesize=10&webp=1').get(
            'data'):
        yield CoinInfo.parse_obj(json_dict)


def fall_coins():
    for json_dict in json_from_page('https://dncapi.bqrank.net/api/concept/coinrisefall?type=0&pagesize=10&webp=1').get(
            'data'):
        yield CoinInfo.parse_obj(json_dict)


def gray_data():
    data = json_from_page('https://dncapi.bqrank.net/api/v3/grayscale/index_list?webp=1').get('data')
    return Data.parse_obj(data)


def test_main():
    data = gray_data()
    for coin in data.list:
        print(f"coin:{coin}")


if __name__ == "__main__":
    test_main()
