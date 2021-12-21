# coding: utf-8

import asyncio
import time
from models import ExecutionTask
from processor import get_stanby_task, update_task_percentage
from uuid import uuid4
from random import randint


async def execution(task: ExecutionTask):
    for i in range(100):
        percent = i + 1
        time.sleep(0.5)
        print(f'{percent}% executed!')
        await update_task_percentage(task.id, percent, uuid4())


async def async_main():
    while True:
        executionTask = await get_stanby_task()
        if executionTask:
            await execution(executionTask)
        else:
            time.sleep(randint(2, 5))


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
