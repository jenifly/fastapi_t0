import logging
from datetime import datetime, timedelta
from functools import partial
from typing import Optional

import jwt
from fastapi import Body, Depends, Header, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_DAYS
from model.responses import RESPONSE_CODE, RESPONSE_RESULT
from model.user import IUser, IUserSImple, IUserInDB
from dependencies.db import DB, get_dbs, Redis, get_redis


class __OAuth2PasswordRequestForm:
    def __init__(
        self,
        grant_type: str = Body(None, regex="password", embed=True),
        username: str = Body(..., embed=True),
        password: str = Body(..., embed=True),
        scope: str = Body("", embed=True),
        client_id: Optional[str] = Body(None, embed=True),
        client_secret: Optional[str] = Body(None, embed=True),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


class OAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        if not authorization and self.auto_error:
            raise HTTPException(401, '无访问许可！')
        return authorization


__pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
__oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/sys/login")


async def __authenticate_user(db: DB, username: str, password: str) -> IUserSImple:
    try:
        user = IUserInDB(**await db.mysql.fetch_one(f"select * from view_user_verify where uid={username}"))
        print(user)
        if not user:
            return False
        if not __pwd_context.verify(password, user.password):
            return False
    except Exception as e:
        print(e)
        return False
    return IUserSImple(**user.dict())


async def __get_current_user(
        db: DB = Depends(get_dbs),
        token: str = Depends(__oauth2_scheme),
        request: Request = None,
        response: Response = None):
    msg = '登录已过期或令牌错误！'
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = IUser(**payload)
        if token_data.role and str(request.url)[-11:] != 'user/logout':
            host = request.client.host
            if host_ := await db.redis.get(f'a-uid-{token_data.uid}'):
                host_ = host_.decode()
            else:
                raise None
            if host_ != host:
                msg = '您的账号已在其他设备登录！'
                raise None
        return token_data
    except:
        response.headers['Authorization'] = ''
        raise HTTPException(402, msg)


def __role_verify(role: tuple, user: IUser = Depends(__get_current_user)):
    for r in role:
        if not user.role >> r & 1:
            raise HTTPException(401, "权限非法！")
    return user


async def login_for_token(
        db: DB = Depends(get_dbs),
        form_data: __OAuth2PasswordRequestForm = Depends(),
        anyway: str = Header(None),
        request: Request = None) -> dict:
    user = await __authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, '用户名或密码错误！')
    host = request.client.host
    if host_ := await db.redis.get(f'a-uid-{user.uid}'):
        host_ = host_.decode()
    if anyway or not host_ or host == host_:
        token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        data = user.dict()
        to_encode = IUser(**data).dict()
        to_encode.update({"exp": datetime.utcnow() + token_expires})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM).decode()
        expires = token_expires.total_seconds()
        await db.mysql.execute(f"INSERT INTO inf_login (uid,host) VALUES ({user.uid},'{host}')")
        await db.redis.setex(f'a-uid-{user.uid}', expires, host)
        data.update({'token': token})
        return RESPONSE_RESULT(data)
    else:
        return RESPONSE_CODE(4001)


async def logout_for_token(
        user: IUser = Depends(__get_current_user),
        redis: Redis = Depends(get_redis),
        response: Response = None):
    response.headers['Authorization'] = ''
    await redis.delete(f'a-uid-{user.uid}')
    return RESPONSE_CODE(4000)


def role_verify(*role: tuple):
    return Depends(partial(__role_verify, role))
