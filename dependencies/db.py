from fastapi import Request
from aioredis import Redis

from core.db import DB, Database


def get_db(request: Request = None) -> DB:
    return request.app.db


def get_mysql(request: Request = None) -> Database:
    return request.app.db.mysql


def get_redis(request: Request = None) -> Redis:
    return request.app.db.redis