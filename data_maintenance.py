# coding: utf-8

import os
from config import DATA_BASE


def list_dirs():
    for dir in os.listdir(DATA_BASE):
        print(dir)

