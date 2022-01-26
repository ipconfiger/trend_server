# coding: utf-8
from typing import List
from pydantic import BaseModel, Field


class TaskImportForm(BaseModel):
    code: str


class TaskForm(BaseModel):
    product: str
    startDate: str
    endDate: str
    taskType: int
    params: str


class EditTaskForm(BaseModel):
    startDate: str
    endDate: str
    params: str


class TaskItem(BaseModel):
    taskId: str
    product: str
    startDate: str
    endDate: str
    taskType: int
    params: str
    processing: bool
    percentage: int
    resultId: str = Field('')


class TaskResponse(BaseModel):
    tasks: List[TaskItem] = Field([], title="可执行任务")
    saved: List[TaskItem] = Field([], title="已保存任务")
    kept: List[TaskItem] = Field([], title="废件箱")


class TaskShareResponse(BaseModel):
    code: str


class LoginForm(BaseModel):
    loginId: str
    password: str
    key: str
    iv: str


class ChangePasswordForm(BaseModel):
    oldPassword: str
    newPassword: str
    oldKey: str
    oldIv: str
    newKey: str
    newIv: str


class BaseResponse(BaseModel):
    code: int
    error: str = Field('')


class LoginResponse(BaseResponse):
    token: str
    expire: int


class WindowItem(BaseModel):
    date: str
    startIdx: int
    startTs: int
    startVal: float
    firstIdx: int
    firstVal: float
    firstTs: int
    highestIdx: int
    highestVal: float
    highestTs: int
    lastIdx: int
    lastVal: float
    lastTs: int


class ResultItem(BaseModel):
    windowCount: int
    successCount: int
    timeUsed: int
    windows: List[WindowItem]


class DetailResponse(BaseResponse):
    task: TaskItem
    result: ResultItem


class Params(BaseModel):
    increment: int
    windowSize: int
    windowUnit: str
