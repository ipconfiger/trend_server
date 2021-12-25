# coding: utf-8
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession

from authorization import check_login, check_token, change_password
from database import get_session
from fastapi.middleware.cors import CORSMiddleware

import datetime

from forms import LoginResponse, LoginForm, TaskResponse, TaskForm, BaseResponse, ChangePasswordForm, EditTaskForm
from processor import add_new_task, task_list, execute_task, delete_exist_task, edit_task_by_id, task_details_by_id, \
    task_daily_image_file, task_daily_window_image_file, task_daily_window_csv_file

app = FastAPI()
security = HTTPBasic()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Status": "It works!"}


def mktime(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    str_dt = '%s%02d%02d%02d%02d%02d' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    # print(fr"{ts} => {str_dt}")
    return int(str_dt)


@app.post('/api/login', response_model=LoginResponse)
async def do_login(form: LoginForm, db: AsyncSession = Depends(get_session)):
    """
    登陆账户
    """
    logging.error(form)
    account, token = await check_login(db, form)
    if account is None:
        logging.error(f"鉴权失败")
        raise HTTPException(status_code=403, detail="鉴权失败")
    logging.error(f"tk:{token.token} expire:{token.expire}")
    return LoginResponse(code=200, token=token.token, expire=token.expire)


@app.post('/api/tasks', response_model=TaskResponse)
async def new_task(form: TaskForm,
                   db: AsyncSession = Depends(get_session),
                   credentials: HTTPBasicCredentials = Depends(security)):
    """
    创建新的任务
    """
    account = await check_token(db, credentials.password)
    if account is None:
        raise HTTPException(status_code=403)
    tasks = await add_new_task(db, form, account)
    return TaskResponse(tasks=tasks)


@app.get('/api/tasks', response_model=TaskResponse)
async def tasks(db: AsyncSession = Depends(get_session),
                credentials: HTTPBasicCredentials = Depends(security)):
    """
    任务列表
    """
    account = await check_token(db, credentials.password)
    if account is None:
        raise HTTPException(status_code=403)
    tasks = await task_list(db, account)
    return TaskResponse(tasks=tasks)


@app.post('/api/task/{task_id}/run', response_model=BaseResponse)
async def run_task(task_id: str, db: AsyncSession = Depends(get_session),
                   credentials: HTTPBasicCredentials = Depends(security)):
    """
    执行任务
    """
    account = await check_token(db, credentials.password)
    if account is None:
        raise HTTPException(status_code=403)
    await execute_task(db, account, task_id)
    return BaseResponse(code=200)


@app.post('/api/task/{task_id}/remove', response_model=BaseResponse)
async def remove_task(task_id: str, db: AsyncSession = Depends(get_session),
                      credentials: HTTPBasicCredentials = Depends(security)):
    """
    删除任务
    """
    account = await check_token(db, credentials.password)
    if account is None:
        raise HTTPException(status_code=403)
    await delete_exist_task(db, account, task_id)
    return BaseResponse(code=200)


@app.post('/api/task/{task_id}/update', response_model=BaseResponse)
async def update_task(task_id: str, form: EditTaskForm, db: AsyncSession = Depends(get_session), credentials: HTTPBasicCredentials = Depends(security)):
    """
    更新任务
    """
    account = await check_token(db, credentials.password)
    if account is None:
        raise HTTPException(status_code=403)
    await edit_task_by_id(db, task_id, form, account)
    return BaseResponse(code=200)


@app.get('/api/task/{task_id}')
async def task_details(task_id: str, db: AsyncSession = Depends(get_session), credentials: HTTPBasicCredentials = Depends(security)):
    """
    获取任务详情
    """
    account = await check_token(db, credentials.password)
    if account is None:
        raise HTTPException(status_code=403)
    return await task_details_by_id(db, task_id)


@app.post('/api/repassword', response_model=BaseResponse)
async def change_my_password(form: ChangePasswordForm, db: AsyncSession = Depends(get_session),
                      credentials: HTTPBasicCredentials = Depends(security)):
    """
    修改密码
    """
    account = await check_token(db, credentials.password)
    if account is None:
        raise HTTPException(status_code=403)
    success = await change_password(db, account, form)
    if success:
        return BaseResponse(code=200)
    raise HTTPException(status_code=500, detail="验证当前密码失败")


@app.get('/api/task/{task_id}/{date}/img')
async def task_daily_image(task_id: str, date: str):
    """
    获取任务每日图片
    """
    return StreamingResponse(task_daily_image_file(task_id, date), media_type="image/jpeg")


@app.get('/api/task/{task_id}/{date}/{idx}/img')
async def task_daily_window_image(task_id: str, date: str, idx: str):
    """
    获取任务每日图片
    """
    return StreamingResponse(task_daily_window_image_file(task_id, date, idx), media_type="image/jpeg")


@app.get('/api/task/{task_id}/{date}/{idx}/csv')
async def task_daily_window_csv(task_id: str, date: str, idx: str):
    """
    获取任务每个window的CSV
    """
    return StreamingResponse(task_daily_window_csv_file(task_id, date, idx), media_type="text/csv")

