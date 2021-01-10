import logging
from datetime import datetime, timedelta

from config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_401_UNAUTHORIZED

from model.respons import RESPONSE_STATUS, ResponseModel
from utils.db_pools import db_pools
from utils.user import (OAuth2PasswordRequestFormJy, User, authenticate_user,
                        create_access_token, get_current_user, oauth2_scheme,
                        update_password)

router = APIRouter()


@router.post("/login", response_model=ResponseModel)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestFormJy = Depends(),
        c: str = Query(None),
        response: Response = None,
        request: Request = None):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="用户名或密码错误！")
    if user.role == 0:
        return {'detail': '登录受限！'}
    host = request.headers['x-forwarded-for']
    if host_ := await db_pools.redis.get(f'a-uid-{user.uid}'):
        host_ = host_.decode()
    print(c, host_, host)
    if c or not host_ or host == host_:
        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=user.dict(), expires_delta=access_token_expires)
        expires = ACCESS_TOKEN_EXPIRE_MINUTES * 86400
        await db_pools.mysql.execute(f"INSERT INTO inf_login (uid,host) VALUES ({user.uid},'{host}')")
        await db_pools.redis.setex(f'a-uid-{user.uid}', expires, host)
        response.set_cookie(key="access_token",
                            value=access_token, expires=expires)
        return RESPONSE_STATUS(4000)
    else:
        return {'status': 4000, 'detail': '您的账号已在其他设备登录，请确认账户安全，是否继续登录？'}


@router.get("/info", response_model=ResponseModel)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {'detail': current_user}


@router.post("/verify", response_model=ResponseModel)
async def verify_me(
        current_user: User = Depends(get_current_user),
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
async def read_users_me(user: User = Depends(get_current_user), response: Response = None):
    response.delete_cookie(key="access_token")
    await db_pools.redis.delete(f'a-uid-{user.uid}')
    return RESPONSE_STATUS(4000)
