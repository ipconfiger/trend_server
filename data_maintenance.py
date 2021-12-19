# coding: utf-8
import datetime
import os
from config import DATA_BASE


def list_dirs():
    for dir in os.listdir(DATA_BASE):
        try:
            dt = datetime.datetime.strptime(dir, '%Y-%m-%d')
            days = (datetime.datetime.now() - dt).days
            print(f'{dir} -> {days}')
        except:
            pass

def main():
    list_dirs()


if __name__ == '__main__':
    main()
