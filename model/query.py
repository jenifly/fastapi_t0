from functools import partial
from enum import Enum

from pydantic import BaseModel
from fastapi import Depends, HTTPException, Request


class QueryType(Enum):
    """
    查询类型枚举
    """
    SE: int = 0
    YM: int = 1


class BaseQuery(BaseModel):
    """
    基础查询参数
    """
    dp: str = ''
    uid: str = ''
    single: bool = False
    field: str = None
    order: str = None
    limit: str = None
    page: int = 1


class DataQuerySE(BaseQuery):
    """
    起始数据查询参数
    """
    start: str
    end: str


class DataQueryMY(BaseQuery):
    """
    月度数据查询参数
    """
    ym: str


def query(e: QueryType, req=Request) -> BaseQuery:
    return Depends(partial(_query, e))


def _query(e: QueryType, req: Request):
    tmp = req.query_params._dict
    page = int(tmp.get('page', 1))
    pageSize = int(tmp.get('pageSize', 20))
    if 'order' in tmp:
        tmp['order'] = tmp['order'][:len(tmp['order'])-3]
    try:
        if e == QueryType.SE:
            if 'uid' not in tmp:
                tmp['limit'] = f'limit {(page - 1) * pageSize},{pageSize}'
            return DataQuerySE(**tmp)
    except:
        raise HTTPException(400, '查询数据非法！')
