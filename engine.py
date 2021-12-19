import datetime
import time
import os
import numpy as np
import statistics
from scripts.bcd_btc import compute
from dataclasses import dataclass
from decimal import Decimal

DIR_BASE = '/home/pi/data'


def load_array(dt: datetime.datetime):
    file_path = os.path.join(DIR_BASE, dt.strftime('%Y-%m-%d'), 'BCD-BTC-candle1m.npy')
    return np.load(file_path)


def load_array2(dt: str):
    file_path = os.path.join(DIR_BASE, dt, 'BCD-BTC-candle1m.npy')
    return np.load(file_path)


def load_array3(product: str, dt: str):
    file_path = os.path.join(DIR_BASE, dt, '%s-tickers.npy' % product)
    return np.load(file_path)


def dates_between(start_date, end_date):
    st = start_date.split(' ')[0]
    ed = end_date.split(' ')[0]
    if st == ed:
        return [st]
    start_day = datetime.datetime.strptime(st, '%Y-%m-%d')
    end_day = datetime.datetime.strptime(ed, '%Y-%m-%d')
    days = [start_day.date(), ]
    for i in range(1, 365):
        next_day = start_day.date() + datetime.timedelta(days=i)
        if next_day < (end_day + datetime.timedelta(days=1)).date():
            days.append(next_day)
        else:
            break
    return days


def dates_to_now(date_str):
    start_day = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    days = [start_day.date(), ]
    for i in range(1, 365):
        next_day = start_day.date() + datetime.timedelta(days=i)
        if next_day < (datetime.datetime.now() + datetime.timedelta(days=1)).date():
            days.append(next_day)
        else:
            break
    return days


def hours_dat(data_array, hours):
    data = []
    for row in data_array:
        ts = row[1]
        dt = datetime.datetime.fromtimestamp(int(ts)/1000)
        if dt.hour in hours:
            data.append(row)
    return data


def data_between(start_dt: str, end_dt: str):
    days = dates_between(start_dt, end_dt)
    start_datetime = datetime.datetime.strptime(start_dt, '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.datetime.strptime(end_dt, '%Y-%m-%d %H:%M:%S')
    start_ts = time.mktime(start_datetime.timetuple())
    end_ts = time.mktime(end_datetime.timetuple())
    day_datas = []
    print(f'start ts:{start_ts} end ts:{end_ts}')
    for d in days:
        day_datas.append(load_array2(d))
    data_rows = []
    if len(days) == 1:
        for r in day_datas[0]:
            # print(f'{start_ts} <= {int(r[1])/1000} <= {end_ts}')
            if start_ts <= int(r[1])/1000 <= end_ts:
                data_rows.append(r)
    return data_rows


def product_data_between(product: str, start_dt: str, end_dt: str):
    print(f'{start_dt} -> {end_dt}')
    days = dates_between(start_dt, end_dt)
    start_datetime = datetime.datetime.strptime(start_dt, '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.datetime.strptime(end_dt, '%Y-%m-%d %H:%M:%S')
    start_ts = time.mktime(start_datetime.timetuple())
    end_ts = time.mktime(end_datetime.timetuple())
    day_datas = []
    print(f'{days}')
    for d in days:
        data = load_array3(product, '%s' % d)
        print(f'load rows:{len(data)}')
        day_datas.append(data)
    data_rows = []
    for day_data in day_datas:
        for r in day_data:
            timestamp = int(r[-1])/1000
            # print(f'{start_ts} <= {int(r[1])/1000} <= {end_ts}')
            if start_ts <= timestamp <= end_ts:
                data_rows.append((int(r[-1])/1000, r[2]))
            else:
                # print(f'PASS: {start_ts} <= {timestamp} <= {end_ts} {start_ts <= timestamp <= end_ts}')
                pass
    return data_rows


class Engine(object):
    def __init__(self, start_date):
        self._start_date = start_date
        self.days = dates_to_now(self._start_date)
        self.last_day = None
        self.this_day = None

    def walk_through(self):
        for i in range(len(self.days)-1):
            self.last_day = self.days[i]
            self.this_day = self.days[i+1]
            self.compute_day()

    def compute_day(self):
        last_day_arr = load_array(self.last_day)
        last_3_hours = hours_dat(last_day_arr, [21, 22, 23])
        start_idx = len(last_3_hours)
        this_day_arr = load_array(self.this_day)
        before_21_arr = hours_dat(this_day_arr, list(range(21)))
        data_arr = last_3_hours + before_21_arr
        self.walk_through_day(start_idx, data_arr)

    def walk_through_day(self, start_idx, day_arr):
        ts = day_arr[start_idx][1]
        for idx in range(start_idx, len(day_arr)):
            compute_data = self.compute_3_hours(idx, day_arr)
            rs = compute(compute_data, [], self.this_day, int(ts)/1000)
            if rs > 0:
                print('买入')
            else:
                if rs < 0:
                    print('卖出')
                else:
                    print('持仓不操作')

    def compute_3_hours(self, idx, day_arr):
        point = int(day_arr[idx][1])/1000
        datas = []
        for i in range(idx):
            real_idx = idx - i
            row = day_arr[real_idx]
            ts = int(row[1])/1000
            if point - ts < 3600 * 3:
                datas.append(row)
            else:
                break
        return datas


@dataclass
class Trade(object):
    ts: int
    trade_type: int
    price: Decimal
    amount: Decimal


class Store(object):
    def __init__(self, init_total, init_cost):
        self.total = init_total
        self.cost = init_cost
        self.tradings = []

    def getHighest(self):
        if len(self.tradings) < 1:
            return self.cost
        if len(self.tradings) < 2:
            return self.tradings[0].price
        return max([trade.price for trade in self.tradings])

    def getLowest(self):
        if len(self.tradings) < 1:
            return self.cost
        if len(self.tradings) < 2:
            return self.tradings[0].price
        return min([trade.price for trade in self.tradings])

    def getMid(self):
        if len(self.tradings) < 1:
            return self.cost
        if len(self.tradings) < 2:
            return self.tradings[0].price
        return statistics.median([trade.price for trade in self.tradings])

    def add_trade(self, trade):
        self.tradings.append(trade)


class AnalysisEngine(object):
    def __init__(self, product, start_date, end_date, increment, window_size):
        self.product = product
        self.start_date = start_date
        self.end_date = end_date
        self.increment = increment
        self.window_size = window_size
        self.data = []
        self.windows = []

    def compute_window(self, window):
        start_ts, start_val = window[0]
        last_ts, last_val = window[-1]
        waves = []
        wave = []
        level = float(start_val) * (100 + int(self.increment))/100.0
        for ts, val in window:
            if float(val) >= level:
                wave.append((ts, val))
            else:
                if wave:
                    waves.append(wave)
                    wave = []
        if waves:
            self.windows.append([start_ts, last_ts, waves])

    def run(self):
        self.data = product_data_between(self.product, self.start_date, self.end_date)
        window = []
        current_ts, _ = self.data[0]
        for ts, val in self.data:
            if ts - current_ts < int(self.window_size) * 60:
                window.append((ts, val))
            else:
                # windows.append(window)
                self.compute_window(window)
                window = [(ts, val), ]
                current_ts = ts
        else:
            if window:
                # windows.append(window)
                self.compute_window(window)


class ComputeEngine(object):
    def __init__(self, data, init_position=0, step=0, init_hold_amount=0, init_cost=0):
        self.data_array = data
        self.position = init_position
        self.step = step
        self.hold_amount = init_hold_amount
        self.store = Store(self.hold_amount, init_cost)

    def walk(self):
        temp = []
        for r in self.data_array:
            for row in self.data_array:
                start_ts = int(r[1])/1000
                current_ts = int(row[1])/1000
                if current_ts - start_ts > self.step:
                    break
                else:
                    temp.append(r)
            yield temp
            temp = []
        if temp:
            yield temp

    def compute(self):
        for data in self.walk():
            print(f'data:{len(data)}')
            self.pre_compute(data)

    def pre_compute(self, data_arr):
        """
        high, low, cost, mid, h_price, l_price
        :param data_arr:
        :return:
        """
        numbers = [Decimal(r[2]) for r in data_arr]
        avg = statistics.mean(numbers)
        desc_numbers = sorted(list(set(numbers)), reverse=True)
        asc_numbers = sorted(list(set(numbers)), reverse=False)
        high = desc_numbers[:5]
        low = asc_numbers[:5]

        highest = self.store.getHighest()
        lowest = self.store.getLowest()
        mid = self.store.getMid()

        print(f'avg:{avg} hight:{high} low:{low} total:{self.store.total}')
        state = compute(data_arr, avg, high, low, self.store.total, self.store.cost, mid, highest, lowest)
        if state == 1:
            print('买')
            self.store.add_trade(Trade(
                ts=int(int(data_arr[-1][1])/1000),
                trade_type=1,
                price=Decimal(data_arr[-1][2]),
                amount=Decimal(data_arr[-1][2]) * 5))
        if state == 0:
            print('啥都不做')
        if state == -1:
            print('卖')
            self.store.add_trade(Trade(
                ts=int(int(data_arr[-1][1]) / 1000),
                trade_type=-1,
                price=Decimal(data_arr[-1][2]),
                amount=Decimal(data_arr[-1][2]) * 5))


def main():
    Engine('2021-09-21').walk_through()


if __name__ == '__main__':
    main()




