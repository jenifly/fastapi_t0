import logging
from datetime import datetime, timedelta
from functools import partial
from typing import Optional

import jwt
from fastapi import Body, Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_402_PAYMENT_REQUIRED

from core.config import ALGORITHM, SECRET_KEY
from model.user import IUser, IUserInDB
from dependencies.db import get_db, DB


class OAuth2PasswordRequestFormJy:
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


class OAuth2PasswordJy(OAuth2PasswordBearer):
    async def __call__(self, Authorization: str = Header(None)) -> Optional[str]:
        if not Authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_402_PAYMENT_REQUIRED,
                    detail="登录已过期！",
                )
            else:
                return None
        return Authorization


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordJy(tokenUrl="/api/v1/user/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def update_password(username, password):
    return await db_pools.mysql.execute(
        f"update user set `password`='{pwd_context.hash(password)}' where id={username}")


async def authenticate_user(username: str, password: str):
    try:
        user = IUserInDB(**await db_pools.mysql.fetch_one(
            f"select * from view_user_verify where uid={username}"))
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
    except Exception as e:
        logging.error(e)
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM).decode()


async def get_current_user(token: str = Depends(oauth2_scheme), request: Request = None):
    credentials_exception = HTTPException(status_code=HTTP_402_PAYMENT_REQUIRED,
                                          detail="凭据已过期或错误，重复尝试将锁定ip！")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("uid")
        if payload.get('role') > 0 and str(request.url)[-11:] != 'user/logout':
            host = request.headers['host']
            if host_ := await db_pools.redis.get(f'a-uid-{username}'):
                host_ = host_.decode()
            if host_ != host:
                credentials_exception = HTTPException(status_code=HTTP_402_PAYMENT_REQUIRED,
                                                      detail="您的账号已在其他设备登录，")
                raise credentials_exception
        if username is None:
            raise credentials_exception
        token_data = IUser(**payload)
    except PyJWTError:
        raise credentials_exception
    if token_data is None:
        raise credentials_exception
    return token_data


def role_verify(*role: tuple) -> Depends:
    def verify(user: IUser = Depends(get_current_user)) -> IUser:
        for r in role:
            if not user.role >> r & 1:
                raise HTTPException(401, "权限非法！")
        return user

    return Depends(verify)


# def __role_verify(role: tuple, user: IUser = Depends(get_current_user)):
#     for r in role:
#         if not user.role >> r & 1:
#             raise HTTPException(401, "权限非法！")
#     return user
