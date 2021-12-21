# coding: utf-8

import asyncio

from models import ExecutionTask
from processor import get_stanby_task


def execution(task: ExecutionTask, update_percentage):
    pass


async def async_main():
    while True:
        executionTask = await get_stanby_task()
        execution(executionTask, )


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
