import logging

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import Response
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from config import ACCESS_TOKEN_EXPIRE_MINUTES
from model.response import RESPONSE_STATUS, ResponseModel
from utils.user_verify import IUser, oauth2_scheme, authenticate_user, create_access_token, get_current_user, OAuth2PasswordRequestFormJy, update_password
from utils.db_pools import db_pools


router = APIRouter()


@router.post("/login", response_model=ResponseModel)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestFormJy = Depends(),
        c: str = Query(None),
        request: Request = None):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="用户名或密码错误！")
    host = request.headers['host']
    if host_ := await db_pools.redis.get(f'a-uid-{user.uid}'):
        host_ = host_.decode()
    if c or not host_ or host == host_:
        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = user.dict()
        access_token = create_access_token(
            data=data, expires_delta=access_token_expires)
        expires = ACCESS_TOKEN_EXPIRE_MINUTES * 86400
        await db_pools.mysql.execute(f"INSERT INTO inf_login (uid,host) VALUES ({user.uid},'{host}')")
        await db_pools.redis.setex(f'a-uid-{user.uid}', expires, host)
        data.update({'token': access_token})
        del data['password']
        return {'detail': data}
    else:
        return {'status': 4000, 'detail': '您的账号已在其他设备登录，请确认账户安全，是否继续登录？'}


@router.get("/info", response_model=ResponseModel)
async def read_users_me(current_user: IUser = Depends(get_current_user)):
    return {'detail': current_user}


@router.post("/verify", response_model=ResponseModel)
async def verify_me(
        current_user: IUser = Depends(get_current_user),
        request: Request = None):
    d = await request.json()
    if 'password' not in d:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="参数非法！"
        )
    if await authenticate_user(current_user.uid, d['password']):
        if 'password_n' in d:
            if await update_password(current_user.uid, d['password_n']):
                return RESPONSE_STATUS(4000)
            else:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="密码修改失败！")
        else:
            return RESPONSE_STATUS(4000)
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="密码校验错误！")


@router.get("/logout", response_model=ResponseModel)
async def read_users_me(user: IUser = Depends(get_current_user), response: Response = None):
    response.delete_cookie(key="access_token")
    await db_pools.redis.delete(f'a-uid-{user.uid}')
    return RESPONSE_STATUS(4000)
