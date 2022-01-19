# coding: utf-8

import io
import random
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_sugar import select, delete

from config import STATIC_BASE
from database import SyncDbWrapper
from forms import TaskForm, TaskItem, EditTaskForm, DetailResponse, ResultItem, WindowItem
from models import ExecutionTask, Account, ExecutionResult, DataWindow, ShareRequest
from uuid import UUID

from utilities.data_processor import date_range


async def add_new_task(db: AsyncSession, form: TaskForm, user: Account):
    """
    添加新的任务
    """
    db.add(ExecutionTask(accountId=user.id,
                         product=form.product,
                         startDate=form.startDate,
                         endDate=form.endDate,
                         increment=form.increment,
                         windowSize=form.windowSize,
                         windowUnit=form.windowUnit))
    await db.flush()
    return await task_list(db, user)


async def edit_task_by_id(db: AsyncSession, task_id: str, form: EditTaskForm, user: Account):
    """
    修改任务属性，方便重新算
    """
    executionTask = await db.get(ExecutionTask, UUID(task_id))
    if executionTask.accountId != user.id:
        return
    executionTask.startDate = form.startDate
    executionTask.endDate = form.endDate
    executionTask.increment = int(form.increment)
    executionTask.windowSize = int(form.windowSize)
    executionTask.windowUnit = form.windowUnit
    await db.flush()


async def task_details_by_id(db: AsyncSession, task_id: str):
    """
     任务详情
    """
    task = await db.get(ExecutionTask, UUID(task_id))
    executionResult = await db.get(ExecutionResult, task.resultId)
    windows = await select(DataWindow).where(DataWindow.resultId == executionResult.id).scalars(db)
    return DetailResponse(code=200, task=TaskItem(
        taskId="%s" % task.id,
        product=task.product,
        startDate=task.startDate,
        endDate=task.endDate,
        increment=task.increment,
        windowSize=task.windowSize,
        windowUnit=task.windowUnit,
        processing=task.processing,
        percentage=task.percentage,
        resultId=''
    ), result=ResultItem(
        windowCount=executionResult.windowCount,
        successCount=executionResult.successCount,
        timeUsed=executionResult.eslapshed,
        windows=[WindowItem(
            date=dataWindow.date,
            startIdx=dataWindow.startIdx,
            startTs=dataWindow.startTs,
            startVal=dataWindow.startVal,
            firstIdx=dataWindow.firstIdx,
            firstVal=dataWindow.firstVal,
            firstTs=dataWindow.firstTs,
            highestIdx=dataWindow.highestIdx,
            highestVal=dataWindow.highestVal,
            highestTs=dataWindow.highestTs,
            lastIdx=dataWindow.lastIdx,
            lastVal=dataWindow.lastVal,
            lastTs=dataWindow.lastTs,
        ) for dataWindow in windows]
    ))


async def fromatResult(db: AsyncSession, task: ExecutionTask):
    if task.percentage < 100:
        if task.percentage > 0:
            return f"执行中：{task.percentage} % ..."
        else:
            if task.percentage<0:
                errorMap = {
                    -404: '数据文件缺失，请检查有选择日期的数据'
                }
                return errorMap[task.percentage]
            else:
                return "未开始"
    else:
        executionResult = await db.get(ExecutionResult, task.resultId)

        return f'共{executionResult.windowCount}/成功{executionResult.successCount} 成功率:{int(executionResult.successCount * 100 / executionResult.windowCount)}%'


async def task_list(db: AsyncSession, user: Account):
    """
    任务列表
    """
    task_items = []
    for task in await select(ExecutionTask).where(
            ExecutionTask.accountId == user.id
    ).order_by(ExecutionTask.create_ts.desc()).scalars(db):
        task_items.append(
            TaskItem(taskId='%s' % task.id, product=task.product, startDate=task.startDate, endDate=task.endDate,
                     increment=task.increment,
                     windowSize=task.windowSize, windowUnit=task.windowUnit, processing=task.processing,
                     percentage=task.percentage, resultId=await fromatResult(db, task)))
    return task_items


async def execute_task(db: AsyncSession, user: Account, task_id: str):
    """
    执行任务
    """
    task = await db.get(ExecutionTask, UUID(task_id))
    if task.accountId != user.id:
        return
    task.processing = True
    task.percentage = 0


async def execute_all_task(db: AsyncSession, user: Account):
    for task in await select(ExecutionTask).where(
            ExecutionTask.accountId == user.id
    ).scalars(db):
        task.processing = True
        task.percentage = 0


async def delete_exist_task(db: AsyncSession, user: Account, task_id: str):
    """
    移除任务
    """
    task = await db.get(ExecutionTask, UUID(task_id))
    if task.accountId != user.id:
        return
    if task.processing:
        return
    await db.delete(task)


def get_stanby_task():
    """
    获取可以执行的任务
    """
    with SyncDbWrapper() as db:
        task = db.query(ExecutionTask).filter(ExecutionTask.processing == True,
                                              ExecutionTask.percentage < 1,
                                              ).order_by(ExecutionTask.create_ts.asc()).first()
        if task:
            task.percentage = 1
            return task


def update_task_percentage(db, task_id: UUID, percentage: int, resultId: UUID):
    """
    更新任务的执行进度
    """
    executionTask = db.query(ExecutionTask).get(task_id)
    executionTask.percentage = percentage
    if percentage > 99:
        executionTask.processing = False
        executionTask.resultId = resultId


def task_daily_image_file(task_id: str, date: str):
    """
    读取任务某日期的图片
    """
    with open(fr'{STATIC_BASE}/day/{task_id}-{date}.jpg', 'rb') as f:
        return io.BytesIO(f.read())


def task_daily_window_image_file(task_id: str, date: str, idx: str):
    """
    读取任务某日期的图片
    """
    with open(fr'{STATIC_BASE}/window/{task_id}-{date}-{idx}.jpg', 'rb') as f:
        return io.BytesIO(f.read())


def task_daily_window_csv_file(task_id: str, date: str, idx: str):
    """
    读取任务某日期的CSV文件
    """
    with open(fr'{STATIC_BASE}/window/{task_id}-{date}-{idx}.csv', 'rb') as f:
        return io.BytesIO(f.read())


async def fork_task_request(db: AsyncSession, user: Account, task_id: str):
    """
    复制任务
    """
    for i in range(100):
        code = "".join(random.sample('qazxswedcvfrtgbnhyujmkiolp1234567890QAZXSWEDCVFRTGBNHYUJMKIOLP', 6))
        if list(await select(ShareRequest).where(ShareRequest.code == code).scalars(db)):
            continue
        task = await db.get(ExecutionTask, UUID(task_id))
        db.add(ShareRequest(accountId=user.id, taskId=task.id, resultId=task.resultId, code=code))
        await db.flush()
        return code


async def fork_task_execute(db: AsyncSession, user: Account, code: str):
    """
    执行复制任务
    """
    for shareRequest in await select(ShareRequest).where(ShareRequest.code == code).scalars(db):
        task = await db.get(ExecutionTask, shareRequest.taskId)
        result = await db.get(ExecutionResult, shareRequest.resultId)
        newTask = ExecutionTask(
            accountId=user.id,
            product=task.product,
            startDate=task.startDate,
            endDate=task.endDate,
            increment=task.increment,
            windowSize=task.windowSize,
            windowUnit=task.windowUnit,
            percentage=100
        )
        db.add(newTask)
        await db.flush()
        newResult = ExecutionResult(
            accountId=user.id,
            taskId=newTask.id,
            windowCount=result.windowCount,
            successCount=result.successCount,
            eslapshed=result.eslapshed
        )
        db.add(newResult)
        await db.flush()
        dates = date_range(task.startDate, task.endDate)
        for date_str in dates:
            from_path = fr'{STATIC_BASE}/day/{task.id}-{date_str}.jpg'
            to_path = fr'{STATIC_BASE}/day/{newTask.id}-{date_str}.jpg'
            shutil.copyfile(from_path, to_path)
        idx = 0
        for dataWindow in await select(DataWindow).where(
                DataWindow.taskId == task.id, DataWindow.resultId == result.id).scalars(db):
            db.add(
                DataWindow(
                    accountId=user.id,
                    taskId=newTask.id,
                    resultId=newResult.id,
                    date=dataWindow.date,
                    file_path=dataWindow.file_path,
                    startIdx=dataWindow.startIdx,
                    startTs=dataWindow.startTs,
                    startVal=dataWindow.startVal,
                    firstIdx=dataWindow.firstIdx,
                    firstVal=dataWindow.firstVal,
                    firstTs=dataWindow.firstTs,
                    highestIdx=dataWindow.highestIdx,
                    highestVal=dataWindow.highestVal,
                    highestTs=dataWindow.highestTs,
                    lastIdx=dataWindow.lastIdx,
                    lastVal=dataWindow.lastVal,
                    lastTs=dataWindow.lastTs,
                )
            )
            csv_from_path = fr'{STATIC_BASE}/window/{task.id}-{dataWindow.date}-{idx}.csv'
            img_from_path = fr'{STATIC_BASE}/window/{task.id}-{dataWindow.date}-{idx}.jpg'
            csv_to_path = fr'{STATIC_BASE}/window/{newTask.id}-{dataWindow.date}-{idx}.csv'
            img_to_path = fr'{STATIC_BASE}/window/{newTask.id}-{dataWindow.date}-{idx}.jpg'
            shutil.copyfile(csv_from_path, csv_to_path)
            shutil.copyfile(img_from_path, img_to_path)
        newTask.resultId = newResult.id
        await db.delete(shareRequest)
        await db.flush()
        return


