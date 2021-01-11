import pandas as pd
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from model.responses import ResponseModel
from utils.sys import login_for_token, logout_for_token


router = APIRouter()


@router.post('/login', response_model=ResponseModel)
def login(res: dict = Depends(login_for_token)):
    return res


@router.get("/logout", response_model=ResponseModel)
async def logout(res: dict = Depends(logout_for_token)):
    return res
