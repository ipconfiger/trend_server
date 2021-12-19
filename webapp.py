# coding: utf-8

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from engine import AnalysisEngine
from fastapi.middleware.cors import CORSMiddleware

import datetime


class FetchRequest(BaseModel):
    product: str
    fromDateTime: str
    toDateTime: str
    increment: int
    timeWindow: int


class Ticker(BaseModel):
    dateTime: int
    value: float


class Wave(BaseModel):
    first: int               # 第一个超过涨幅的点
    firstVal: float          # 第一个超过涨幅点的值
    highest: int             # 最高点
    highestVal: float        # 最高点的值
    last: int                # 回落低于涨幅的第一个点
    lastVal: float           # 回落低于涨幅的值


class Windows(BaseModel):
    start: int               # 时间段开始时间
    end: int                 # 时间段结束时间
    waves: List[Wave]        # 包含的波


class DataResponse(BaseModel):
    ticks: List[Ticker]      # 数据段列表
    windows: List[Windows]   # 时间段列表


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Status": "It works!"}


def mktime(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    str_dt = '%s%02d%02d%02d%02d%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    # print(fr"{ts} => {str_dt}")
    return int(str_dt)


@app.post('/exec', response_model=DataResponse)
def execute(form: FetchRequest):
    engine = AnalysisEngine(form.product, form.fromDateTime, form.toDateTime, form.increment, form.timeWindow)
    engine.run()
    ticks = []
    window_list = []
    for ts, val in engine.data:
        # print(f'data: {ts} {val}')
        ticks.append(Ticker(dateTime=mktime(ts), value=float(val)))

    for start_ts, end_ts, waves in engine.windows:
        wave_list = []
        for wave in waves:
            first_ts, first_val = wave[0]
            last_ts, last_val = wave[-1]
            max_val = max([float(val) for _, val in wave])
            max_ts = [_ts for _ts, _val in wave if float(_val) == max_val][0]
            wave_list.append(Wave(first=mktime(first_ts), firstVal=float(first_val), highest=mktime(max_ts),
                                  highestVal=max_val, last=mktime(last_ts), lastVal=float(last_val)))
        windows = Windows(start=mktime(start_ts), end=mktime(end_ts), waves=wave_list)
        window_list.append(windows)
    response = DataResponse(ticks=ticks, windows=window_list)
    return response



