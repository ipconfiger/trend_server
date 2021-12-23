import datetime
import os

import numpy as np
from typing import List
from decimal import Decimal
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
from sqlalchemy.ext.asyncio import AsyncSession

from config import DATA_BASE, STATIC_BASE
from models import ExecutionTask, ExecutionResult, DataWindow


class Result(object):
    def __init__(self):
        self.windowCount = 0
        self.successCount = 0
        self.windows = []


class Window(object):
    def __init__(self):
        self.date = ''
        self.init_idx = 0
        self.init_ts = 0
        self.init_val = 0
        self.first_idx = 0
        self.first_ts = 0
        self.first_val = 0
        self.highest_idx = 0
        self.highest_ts = 0
        self.highest_val = 0
        self.last_idx = 0
        self.last_ts = 0
        self.last_val = 0
        self.arr = []


def date_range(startDate: str, endDate: str) -> List[str]:
    """
    获取待执行的时间范围
    """
    dt = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    dates = []
    for i in range(365):
        if i:
            current_dt = (dt + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(current_dt)
            if current_dt == endDate:
                break
        else:
            dates.append(startDate)
    return dates


def data_file_path(product, date_str):
    return f'{date_str}/{product}-tickers.npy'


def comput_window(arr, increment):
    origin_v = arr[0][1]
    level_flag = origin_v * (100 + Decimal(increment)) / 100
    # print(f'origin:{origin_v} flag:{level_flag}')
    first_ts, first_val, first_idx = 0, 0, 0
    highest_ts, highest_val, highest_idx = 0, 0, 0
    last_ts, last_val, last_idx = 0, 0, 0
    current_val = 0
    max_val = max([v for _, v in arr])
    for idx, tp in enumerate(arr):
        ts, v = tp
        # print(f'cv:{level_flag - v}')
        if first_ts < 1:
            if v >= level_flag:
                first_ts, first_val, first_idx = ts, v, idx
        else:
            if first_ts and highest_ts < 1:
                if v == max_val:
                    highest_ts, highest_val, highest_idx = ts, v, idx
                if v < level_flag:
                    first_ts, first_val, first_val = 0, 0, 0
            if first_ts and highest_ts:
                if v <= level_flag:
                    last_ts, last_val, last_idx = ts, v, idx
                    break

    if first_idx and highest_idx:
        window = Window()
        window.init_idx = 0
        window.init_ts = arr[0][0]
        window.init_val = origin_v
        window.first_idx = first_idx
        window.first_ts = first_ts
        window.first_val = first_val
        window.highest_idx = highest_idx
        window.highest_ts = highest_ts
        window.highest_val = highest_val
        window.last_idx = last_idx
        window.last_ts = last_ts
        window.last_val = last_val
        return window
    return None


def cut(arr, start_idx, increment, window_size, window_unit):
    coefficient = {'m': 60, 'h': 3600}[window_unit]
    time_offset = coefficient * window_size
    next_idx = 0
    end_idx = 0
    sub_arr = []
    for idx, tp in enumerate(arr[start_idx:]):
        ts, v = tp
        sub_arr.append((ts, v))
        if ts - arr[start_idx][0] <= 60000:
            next_idx = idx
        if (ts - arr[start_idx][0]) >= time_offset * 1000:
            end_idx = idx
            break
    window = comput_window(sub_arr, increment)
    if window:
        if window.last_idx:
            window.init_idx += start_idx
            window.first_idx += start_idx
            window.highest_idx += start_idx
            window.last_idx += start_idx
            return window, start_idx + end_idx
        else:
            return window, start_idx + end_idx
    else:
        return None, start_idx + (next_idx or 3)


def draw_window(arr, color):
    plt.title("Window")
    plt.xlabel("时")
    plt.ylabel("值")
    x = [datetime.datetime.fromtimestamp(int(ts / 1000)) for ts, _ in arr]
    y = [v for _, v in arr]
    max_y = max(y)
    min_y = min(y)
    plt.ylim(min_y * Decimal("0.95"), max_y * Decimal("1.1"))
    plt.plot_date(x, y, color=color, linewidth=0.5, linestyle='solid', marker=',')
    return max_y / Decimal("10.0")


def draw_stack_window(arr, color, window, scale):
    tmp = datetime.datetime.fromtimestamp(window.init_ts / 1000)
    dt = datetime.datetime(tmp.year, tmp.month, tmp.day, 0, 0, 0)
    plt.stackplot([datetime.datetime.fromtimestamp(int(ts / 1000)) for ts, _ in arr], [v for _, v in arr], color=color)
    plt.scatter(datetime.datetime.fromtimestamp(window.first_ts / 1000), window.first_val, )
    plt.scatter(datetime.datetime.fromtimestamp(window.highest_ts / 1000), window.highest_val, )
    plt.scatter(datetime.datetime.fromtimestamp(window.last_ts / 1000), window.last_val, )
    plt.text(datetime.datetime.fromtimestamp(window.first_ts / 1000), window.first_val + scale, '%s' % window.first_val,
             va='top', ha='center')
    plt.text(datetime.datetime.fromtimestamp(window.highest_ts / 1000), window.highest_val + scale,
             '%s' % window.highest_val, va='top', ha='center')
    plt.text(datetime.datetime.fromtimestamp(window.last_ts / 1000), window.last_val + scale, '%s' % window.last_val,
             va='top', ha='center')
    plt.plot_date([dt, datetime.datetime.fromtimestamp(window.first_ts / 1000)], [window.first_val, window.first_val],
                  linestyle='--', c='b')


def save_window(db: AsyncSession, task: ExecutionTask, window: Window, result: ExecutionResult):
    """
    保存窗口信息
    """
    dataWindow = DataWindow(accountId=task.accountId,
                            taskId=task.id,
                            resultId=result.id,
                            date=window.date,
                            file_path='',
                            startIdx=window.init_idx,
                            startVal=window.init_val,
                            startTs=window.init_ts,
                            firstIdx=window.first_idx,
                            firstVal=window.first_val,
                            firstTs=window.first_ts,
                            highestIdx=window.highest_idx,
                            highestVal=window.highest_val,
                            highestTs=window.highest_ts,
                            lastIdx=window.last_idx,
                            lastVal=window.last_val,
                            lastTs=window.last_ts
                            )
    db.add(dataWindow)


def proccess_oneday(taskId, data, date, increment: int, window_size: int, window_unit: str):
    result = Result()
    arr = []
    for idx, r in enumerate(data):
        ts = int(r[-1])
        v = Decimal(r[2])
        arr.append((ts, v))
    start_idx = 0
    color_idx = 0
    colors = [v for k, v in mcolors.CSS4_COLORS.items()]
    draw_window(arr, 'k')
    while True:
        os_start = start_idx
        window, end_idx = cut(arr, start_idx, increment, window_size, window_unit)
        if window:
            result.windowCount += 1
            if window.last_idx:
                color_idx += 1
                draw_stack_window(arr[window.init_idx: window.last_idx], colors[color_idx], window, 1)
                result.successCount += 1
                window.arr = arr[window.init_idx: window.last_idx].copy()
                window.date = date
                result.windows.append(window)
                print(
                    f'i:{window.init_idx}-{window.init_val} f:{window.first_idx}-{window.first_val} h:{window.highest_idx}-{window.highest_val} l:{window.last_idx}-{window.last_val}')
        if end_idx >= len(arr) - 1:
            break
        else:
            start_idx = end_idx
            # print(f'Next start: {end_idx}')
        if os_start == end_idx:
            break
    plt.tick_params(top='off', right='off')
    filePath = os.path.join(STATIC_BASE, 'day', f'{taskId}-{date}.jpg')
    plt.savefig(filePath)
    print(f"Result: w:{result.windowCount} success:{result.successCount}")
    return result


def init_plt():
    plt.figure(figsize=(90, 20), dpi=160)


def reinit_plt():
    plt.clf()
    init_plt()


def main():
    plt.figure(figsize=(90, 20), dpi=160)
    date = '2021-12-18'
    path = '/Users/alex/Projects/temp/trend_data/data/' + data_file_path('ZEC-USDT', date)
    data = np.load(path)
    proccess_oneday('testId', data, date, 2, 60, 'm')


if __name__ == "__main__":
    main()
