# coding: utf-8
import datetime
import os
from config import DATA_BASE


def list_dirs():
    for dir in os.listdir(DATA_BASE):
        try:
            dt = datetime.datetime.strptime(dir, '%Y-%m-%d')
            days = (datetime.datetime.now() - dt).days
            if days > 6:
                yield dir
        except:
            pass


def main():
    for dir in list_dirs():
        print(f'{DATA_BASE}/{dir}')


if __name__ == '__main__':
    main()
