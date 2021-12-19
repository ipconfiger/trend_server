# coding: utf-8
import os
import numpy as np
import datetime
import logging
from config import DATA_BASE

#DATA_BASE = '/Users/alex/Projects/temp/data_sync/data'
#DATA_BASE = '/home/pi/data'


def get_now():
    return datetime.datetime.now(tz=datetime.timezone(offset=datetime.timedelta(hours=8)))


def gen_file_path(product_name, chn):
    now = get_now()
    folder_path = os.path.join(DATA_BASE, datetime.date.strftime(now, "%Y-%m-%d"))
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return os.path.join(folder_path, f"{product_name}-{chn}.npy")


HOLDERS = {}


class DataHolder(object):
    def __init__(self, product_name, chn):
        self.data = []
        self.chn = chn
        self.product_name = product_name
        self.reload()
        self.date = get_now().date().strftime('%Y-%d-%m')

    def reload(self):
        file_path = gen_file_path(self.product_name, self.chn)
        try:
            ndarr = np.load(file_path)
            self.data = ndarr.tolist()
        except Exception as ex:
            logging.error(f"加载数据Error：{ex}")

    def check_date(self):
        today = get_now().date().strftime('%Y-%d-%m')
        if today != self.date:
            del self.data[:]
            self.date = today

    def append(self, *row):
        self.check_date()
        self.data.append(row)
        np.save(gen_file_path(self.product_name, self.chn), self.data)


def get_holder(product_name:str, chn:str) -> DataHolder:
    key = f"{product_name}:{chn}"
    if key not in HOLDERS:
        HOLDERS[key] = DataHolder(product_name, chn)
    return HOLDERS[key]


