# coding: utf-8
from typing import List
from pydantic import BaseModel, Field


class TaskForm(BaseModel):
    product: str
    startDate: str
    endDate: str
    increment: int
    windowSize: int
    windowUnit: str


class TaskItem(BaseModel):
    taskId: str
    product: str
    startDate: str
    endDate: str
    increment: int
    windowSize: int
    windowUnit: str
    processing: bool
    percentage: int
    resultId: str = Field('')


class TaskResponse(BaseModel):
    tasks: List[TaskItem]


class LoginForm(BaseModel):
    loginId: str
    password: str
    key: str
    iv: str


class BaseResponse(BaseModel):
    code: int
    error: str = Field('')


class LoginResponse(BaseResponse):
    token: str
    expire: int
