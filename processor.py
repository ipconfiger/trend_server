# coding: utf-8

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_sugar import select, delete

from database import DbWrapper
from forms import TaskForm, TaskItem
from models import ExecutionTask, Account
from uuid import UUID


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
                     percentage=task.percentage, resultId=task.resultId or ''))
    return task_items


async def execute_task(db: AsyncSession, user: Account, task_id: str):
    """
    执行任务
    """
    task = await db.get(ExecutionTask, UUID(task_id))
    if task.accountId != user.id:
        return
    task.processing = True


async def remove_task(db: AsyncSession, user: Account, task_id: str):
    """
    移除任务
    """
    task = await db.get(ExecutionTask, UUID(task_id))
    if task.accountId != user.id:
        return
    if task.processing:
        return
    await db.delete(task)


async def get_stanby_task():
    """
    获取可以执行的任务
    """
    async with DbWrapper() as db:
        return await select(ExecutionTask).where(ExecutionTask.processing == True,
                                                 ExecutionTask.percentage > 0
                                                 ).order_by(ExecutionTask.create_ts.asc()).first(db)


async def update_task_percentage(task_id: str, percentage: int):
    """
    更新任务的执行进度
    """
    async with DbWrapper() as db:
        executionTask = await db.get(ExecutionTask, UUID(task_id))
        executionTask.percentage = percentage
        if percentage > 99:

