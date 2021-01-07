import logging

from datetime import datetime, timedelta

from fastapi import APIRouter, Body, HTTPException, Query
from starlette.responses import Response
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from config import ACCESS_TOKEN_EXPIRE_MINUTES
from utils.response_modle import RESPONSE_STATUS, ResponseModel
from utils.user_modle import User, role_verify
from utils.db_pools import db_pools

router = APIRouter()



@router.get("", response_model=ResponseModel)
async def read_users_me(
    user: User = role_verify(2),
    limit: str = Query('0,20'),
    total: bool = Query(False)):
    limit = f" limit {limit}"
    data = { 'data': await db_pools.mysql.fetch_all(f"select * from dic_position{limit}") }
    if total:
        data['total'] = (await db_pools.mysql.fetch_one("select count(*) c from dic_position"))['c']
    return {'detail': data}


@router.post('', response_model=ResponseModel)
async def post_group(
    user: User = role_verify(3),
    name: str = Body(...)):
    try:
        return { 'detail': await db_pools.mysql.execute(f"insert into dic_position (name) values ('{name}')") }
    except:
        return { 'detail': 0 }


@router.put('', response_model=ResponseModel)
async def put_group(
    user: User = role_verify(3),
    id: int = Body(...),
    name: str = Body(...)):
    try:
        return { 'detail': await db_pools.mysql.execute(f"update dic_position set name='{name}' where id={id}") }
    except:
        return { 'detail': 0 }


@router.delete('', response_model=ResponseModel)
async def delete_group(
    user: User = role_verify(3),
    id: int = Body(...)):
    return { 'detail': await db_pools.mysql.execute(f"delete from dic_position where id={id}") }
