import logging

from fastapi import APIRouter, Body, Query

from utils.db_pools import db_pools
from utils.response_modle import ResponseModel
from utils.user_modle import User, role_verify

router = APIRouter()


@router.get('', response_model=ResponseModel)
async def get_dp(user: User = role_verify(2),
                 limit: str = Query('0,20'),
                 total: bool = Query(False)):
    limit = f' limit {limit}'
    data = {
        "dp": [{
            'id': user.dp,
            'name': user.dpName
        }] if user.role < 5 else await
        db_pools.mysql.fetch_all(f"select * from dic_department{limit}"),
        "group":
        await db_pools.mysql.fetch_all("select * from dic_group")
    }
    if total:
        data['total'] = 1 if user.role < 5 else (
            await db_pools.mysql.fetch_one("select count(*) c from dic_department"))['c']
    return {'detail': data}


@router.get('/init', response_model=ResponseModel)
async def get_dp(user: User = role_verify(2), ):
    data = {
        "dp": await db_pools.mysql.fetch_all(f"select id,name from dic_department"),
        "group": await db_pools.mysql.fetch_all("select id,name,parents from dic_group"),
        "position": await db_pools.mysql.fetch_all("select id,name from dic_position")
    }
    return {'detail': data}


@router.post('', response_model=ResponseModel)
async def post_dp(user: User = role_verify(2), name: str = Body(...)):
    return {
        'detail':
        await
        db_pools.mysql.execute(f"insert into dic_department(name,uid) values ('{name}',{user.uid}")
    }


@router.put('', response_model=ResponseModel)
async def put_dp(user: User = role_verify(2), dpid: str = Body(...), name: str = Body(...)):
    return {
        'detail':
        await db_pools.mysql.execute(
            f"update dic_department set name='{name}',uid={user.uid} where id='{dpid}'")
    }


@router.delete('', response_model=ResponseModel)
async def delete_dp(user: User = role_verify(2), dpid: str = Body(...)):
    return {'detail': await db_pools.mysql.execute(f"delete from dic_department where id='{dpid}'")}
