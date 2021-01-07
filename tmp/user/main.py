import logging
from datetime import datetime, timedelta

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Path, Query
from fastapi.param_functions import Body
from pymysql.err import IntegrityError

from config import USER_DICT
from model.response import RESPONSE_STATUS, ResponseModel
from utils.db_pools import db_pools, to_df, uinsert
from utils.df_excel_Response import DataFrameResponse
from utils.user_verify import IUser, role_verify

router = APIRouter()


@router.get('', response_model=ResponseModel)
async def read_users_me(
    user: IUser = role_verify(2),
    limit: str = Query('0.20'),
    total: bool = Query(False),
    query: str = Query('')
):
    limit = f" limit {limit}"
    if 'dp' not in query and user.role < 5:
        query = f" and {query}" if query else ''
        query = f"dp='{user.dp}'{query}"
    query = f" where {query}" if query else ''
    data = {
        "data": await db_pools.mysql.fetch_all(f"select * from view_user_detail{query}{limit}")
    }
    if total:
        data['total'] = (await db_pools.mysql.fetch_one(f"select count(*) c from dic_user{query}"))['c']
    return {'detail': data}


@router.post('', response_model=ResponseModel)
async def put_users(
        user: IUser = role_verify(3),
        form: dict = Body(...)):
    form['uid'] = user.uid
    for k in list(form.keys()):
        if not form[k]:
            del form[k]
    try:
        return {'detail': await db_pools.mysql.execute(f"""insert into dic_user ({','.join(k for k in form.keys())}) values ({','.join(f"'{v}'" for v in form.values())})""")}
    except:
        raise HTTPException(400, '该工资号已存在！')


@router.put('', response_model=ResponseModel)
async def put_users(
        user: IUser = role_verify(3),
        form: dict = Body(...)):
    uid = form['id']
    del form['id']
    form['uid'] = user.uid
    for k in list(form.keys()):
        if not form[k]:
            del form[k]
    tmp = ','.join(f"`{k}`='{v}'" for k, v in form.items())
    return {'detail': await db_pools.mysql.execute(f"update dic_user set {tmp} where id={uid}")}


@router.delete('', response_model=ResponseModel)
async def put_users(
        user: IUser = role_verify(3),
        uid: int = Body(...)):
    return {'detail': await db_pools.mysql.execute(f"update dic_user set valid=0 where id={uid}")}


@router.get("/download")
async def get_details(
        user: IUser = role_verify(3),
        query: str = Query('')):
    if 'dp' not in query and user.role < 5:
        query = f" and {query}" if query else ''
        query = f"dp='{user.dp}'{query}"
    query = f" where {query}" if query else ''
    d = to_df(await db_pools.mysql.fetch_all(f"select * from view_user_detail{query}")).drop(['sex', 'dp', 'dp_', 'group', 'position', 'position_', 'role', 'valid', 'status'], axis=1)
    columns = ['工资号', '姓名', '简拼码', '性别', '手机号', '部门', '原部门', '职名', '原职名', '组别',
               '身份证号', '工作证号', '入职年月', '学历', '毕业院校', '专业', '政治面貌', '籍贯', '民族', '地址']
    d.columns = columns
    return DataFrameResponse(d, '人员信息表.xlsx')


@router.post("/upload", response_model=ResponseModel)
async def get_details(user: IUser = role_verify(3), file: bytes = File(...)):
    df = pd.read_excel(file)
    columns = []
    for column in df.columns.values:
        try:
            columns.append(USER_DICT[column])
        except:
            raise HTTPException(
                400, f"<span style='line-height: 28px'>人员表中列名错误：<strong>{column}</strong><br/>有效列名如下：<br/>{list(USER_DICT.keys())}</span>")
    df.columns = columns
    dp = {x[0]: x[1] for x in await db_pools.mysql.fetch_all(f"select name,id from dic_department")}
    ps = {x[0]: x[1] for x in await db_pools.mysql.fetch_all(f"select name,id from dic_position")}
    gp = {x[0]: x[1] for x in await db_pools.mysql.fetch_all(f"select name,id from dic_group")}
    if 'sex' in columns:
        df.sex.replace({'男': 1, '女': 0}, inplace=True)
    if 'dp' in columns:
        df.dp.replace(dp, inplace=True)
    if 'dp_' in columns:
        df.dp_.replace(dp, inplace=True)
    if 'group' in columns:
        df.group.replace(gp, inplace=True)
    if 'position' in columns:
        df.position.replace(ps, inplace=True)
    if 'position' in columns:
        df.position_.replace(ps, inplace=True)
    if 'simple' not in columns:
        pass
    columns = [f'`{col}`' for col in columns]
    s = 0
    for i, row in enumerate(df.itertuples()):
        k = []
        v = []
        for j, c in enumerate(row[1:]):
            if not pd.isna(c):
                k.append(columns[j])
                v.append(str(c).replace('.0', ''))
        try:
            if (await db_pools.mysql.fetch_one(f"select count(*) from dic_user where id={row.id}"))[0]:
                s += await db_pools.mysql.execute(f"""update dic_user set {','.join(f"{k[t]}='{v[t]}'" for t in range(len(k)))} where id={row.id}""")
            else:
                s += await db_pools.mysql.execute(f"""insert into dic_user ({','.join(k)}) values ('{"','".join(v)}')""")
        except IntegrityError as e:
            raise HTTPException(
                400, f"<span style='line-height: 24px'>第 {i + 1} 行<br/>{e}</span>'")
    return {'detail': f'成功更新 {s} 条人员信息！' if s else '无人员信息更新！'}


@router.get('/{k}/{v}', response_model=ResponseModel)
async def read_users_me(
    user: IUser = role_verify(2),
    k: str = Path(...),
    v: str = Path(...)
):
    return {'detail': await db_pools.mysql.fetch_all(f"select * from view_user_detail where {k}='{v}'")}
