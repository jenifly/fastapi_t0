from fastapi import APIRouter, Depends, HTTPException, Body
from utils.response_modle import RESPONSE_STATUS, ResponseModel
from utils.user_modle import User, role_verify
from utils.db_pools import db_pools


router = APIRouter()


@router.post('', response_model=ResponseModel)
async def post_group(
    user: User = role_verify(2),
    parents: str = Body(...),
    name: str = Body(...)):
    return { 'detail': await db_pools.mysql.execute(f"insert into dic_group (name,parents,uid) values ('{name}','{parents}','{user.uid}')") }


@router.put('', response_model=ResponseModel)
async def put_group(
    user: User = role_verify(2),
    gid: int = Body(...),
    parents: str = Body(...),
    name: str = Body(...)):
    return { 'detail': await db_pools.mysql.execute(f"update dic_group set name='{name}',parents='{parents}',uid={user.uid} where id={gid}") }


@router.delete('', response_model=ResponseModel)
async def delete_group(
    user: User = role_verify(2),
    gid: int = Body(...)):
    return { 'detail': await db_pools.mysql.execute(f"delete from dic_group where id={gid}") }