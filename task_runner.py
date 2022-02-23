# coding: utf-8

import time
import logging
from config import DATA_BASE
from database import SyncDbWrapper, Session
from forms import MACDParams
from models import ExecutionTask, ExecutionResult, DataWindow
from processor import get_stanby_task, update_task_percentage
import numpy as np

from utilities.data_processor import date_range, data_file_path, proccess_oneday, save_window, init_plt, reinit_plt, \
    process_macd_one_day, process_macd


def clear():
    with SyncDbWrapper() as db:
        for task in db.query(ExecutionTask).filter(ExecutionTask.processing == True):
            if task.resultId:
                db.query(ExecutionResult).filter(ExecutionResult.id == task.resultId).delete()
                db.query(DataWindow).filter(DataWindow.taskId == task.id).delete()
            task.processing = False
            task.percentage = 0


def get_data(db: Session, task: ExecutionTask, date_str: str, executionResult: ExecutionResult):
    path = DATA_BASE + data_file_path(task.product, date_str)
    try:
        data = np.load(path)
        return data
    except FileNotFoundError as fe:
        logging.error('load data:%s error', path)
        task = db.query(ExecutionTask).get(task.id)
        task.processing = False
        task.percentage = -404
        db.query(DataWindow).filter(DataWindow.resultId == executionResult.id).delete()
        db.query(ExecutionResult).filter(ExecutionResult.id == executionResult.id).delete()
        db.flush()
        db.commit()
        print('exit task execution:%s' % fe)
        return


def execution(task: ExecutionTask):
    dates = date_range(task.startDate, task.endDate)
    total = len(dates)
    startTs = int(time.time() * 1000)
    init_plt()
    with SyncDbWrapper() as db:
        if task.resultId:
            db.query(ExecutionResult).filter(ExecutionResult.id == task.resultId).delete()
            db.query(DataWindow).filter(DataWindow.taskId == task.id).delete()
            db.flush()
        executionResult = ExecutionResult(accountId=task.accountId, taskId=task.id)
        db.add(executionResult)
        db.flush()
        idx = 0
        if task.taskType == 0:
            for date_str in dates:
                data = get_data(db, task, date_str, executionResult)
                if not data:
                    return
                result = proccess_oneday(task.id, data, date_str, task.taskType, task.params)
                executionResult.windowCount = executionResult.windowCount + result.windowCount
                executionResult.successCount = executionResult.successCount + result.successCount
                for window in result.windows:
                    save_window(db, task, window, executionResult)
                idx += 1
                update_task_percentage(db, task.id, int(idx*100.0/total), executionResult.id)
                db.flush()
                db.commit()
                reinit_plt()
        if task.taskType == 1:
            data_arr = []
            for date_str in dates:
                data = get_data(db, task, date_str, executionResult)
                if not data:
                    oneday_data_arr = process_macd_one_day(task.id, data, date_str, MACDParams.parse_raw(task.params))
                    for item in oneday_data_arr:
                        data_arr.append(item)
            process_macd(data_arr, executionResult)

        endTs = int(time.time() * 1000)
        executionResult.eslapshed = endTs - startTs
        db.flush()
        db.commit()


def sync_main():
    clear()
    while True:
        executionTask = get_stanby_task()
        if executionTask:
            execution(executionTask)
        else:
            time.sleep(1)


def main():
    sync_main()


if __name__ == '__main__':
    main()
