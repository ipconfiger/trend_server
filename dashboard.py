# coding=utf-8

import matplotlib
import datetime
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from decimal import Decimal
from engine import data_between, ComputeEngine

matplotlib.use("TkAgg")

START_DATE_TIME = '-START_DATETIME-'
END_DATE_TIME = '-END_DATE_TIME-'
DEFAULT_STEP = '-DEFAULT_STEP-'
DEFAULT_LEVEL = '-DEFAULT_LEVEL-'
HOLD_AMOUNT = '-HOLD_AMOUNT-'
BUTTON_REFRESH = '-BUTTON_REFRESH-'
BUTTON_COMPUTE = '-BUTTON_COMPUTE-'
CANVAS = '-CANVAS-'
FIGURE = '-FIGURE-'
FIGURE_AGG = '-FIGURE_AGG-'
V_LINE = '-V_LINE-'


_VARS = {V_LINE: '0'}

_DATA = []

def current_time_text():
    n = datetime.datetime.now()
    return n.strftime('%Y-%m-%d %H:%M:%S')


def format_ts(ts):
    dt = datetime.datetime.fromtimestamp(int(ts)/1000)
    return f'{dt.hour}:{dt.minute}:{dt.second}'


LeftFrame = [[sg.Canvas(key=CANVAS), ], ]

RightFrame = [
    [sg.Text('开始时间：'), sg.Input(default_text='2021-09-21 18:00:01', key=START_DATE_TIME)],
    [sg.Text('结束时间：'), sg.Input(default_text='2021-09-21 20:00:01', key=END_DATE_TIME)],
    [sg.Text('计算步长：'), sg.Input('600', key=DEFAULT_STEP)],
    [sg.Text('起始成本：'), sg.Input('0.00004086', key=DEFAULT_LEVEL)],
    [sg.Text('起始仓位：'), sg.Input('1', key=HOLD_AMOUNT)],
    [],
    [sg.Button('刷新图形', key=BUTTON_REFRESH), sg.Button('开始演算', key=BUTTON_COMPUTE)],
    [],
    []
]

Layout = [
    [sg.Frame(title='数据曲线', layout=LeftFrame), sg.Frame(title='参数调整', layout=RightFrame)],
    [sg.Table(values=_DATA,
              headings=['交易类型', '交易时间', '交易价格', '交易数量', '复验结果'],
              display_row_numbers=True,
              auto_size_columns=False,
              num_rows=min(25, 2000))]
]


def init_figure():
    if FIGURE not in _VARS:
        print('初始化figure')
        _VARS[FIGURE] = plt.figure()
    return _VARS[FIGURE]


def load_data(fp):
    figure = init_figure()
    array = np.load(fp)
    x = [format_ts(r[1]) for r in array]
    y = [Decimal(r[2]) for r in array]
    plt.plot(x, y)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Trend')
    step = int(len(x) / 10)
    plt.xticks(x[::step], rotation=45)
    return figure


def draw_plots(array):
    figure = init_figure()
    x = [format_ts(r[1]) for r in array]
    y = [Decimal(r[2]) for r in array]
    print(f'x:{len(x)} y:{len(y)}')
    plt.clf()
    plt.plot(x, y)
    plt.plot(x, [Decimal(_VARS[V_LINE]), ] * len(x))
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Trend')
    step = int(len(x) / 10)
    plt.xticks(x[::step], rotation=45)
    return figure


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def refresh_line(window):
    line = load_data('/Users/alex/Projects/temp/data_sync/data/2021-09-21/BCD-BTC-candle1m.npy')
    _VARS[FIGURE_AGG] = draw_figure(window[CANVAS].TKCanvas, line)


def refresh_line_with(window, datas):
    _VARS[FIGURE_AGG].get_tk_widget().forget()
    fig = draw_plots(datas)
    _VARS[FIGURE_AGG] = draw_figure(window[CANVAS].TKCanvas, fig)


def main():
    window = sg.Window('数据验证工具', Layout, size=(1000, 800), finalize=True,
                       element_justification='center',
                       font='Helvetica 18',
                       resizable=True)
    refresh_line(window)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            # 退出
            break
        if event == BUTTON_REFRESH:
            start_str = values[START_DATE_TIME]
            end_str = values[END_DATE_TIME]
            _VARS[V_LINE] = values[DEFAULT_LEVEL]
            datas = data_between(start_str, end_str)
            refresh_line_with(window, datas)
        if event == BUTTON_COMPUTE:
            start_str = values[START_DATE_TIME]
            end_str = values[END_DATE_TIME]
            _VARS[V_LINE] = values[DEFAULT_LEVEL]
            datas = data_between(start_str, end_str)
            engine = ComputeEngine(datas, init_position=Decimal(_VARS[V_LINE]), step=int(values[DEFAULT_STEP]))
            engine.compute()

    window.close()


if __name__ == '__main__':
    main()
