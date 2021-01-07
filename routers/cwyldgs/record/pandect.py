import pandas as pd
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from model.query import DataQuerySE, QueryType, query
from model.response import ResponseModel
from utils.db_pools import db_pools
from utils.df_excel_Response import DataFrameResponse
from utils.user_verify import IUser, role_verify

# from utils.record import get_params

router = APIRouter()


def base_sql(params):
    sql = 'SELECT a.id,'
    sql += 'b.uid,b.name,b.loc,' if params.uid or params.single else 'GROUP_CONCAT(b.uid) uid,GROUP_CONCAT(b.name) name,'
    sql += 'jx,jh,dp,cc,a.pay_date date,sf,zd,jgdm,cq,jc,cd,kc,dd,rd,jc_,tq,dcdd,gs,zxgl FROM dat_gs_zc_detail a left join dat_gs_zc b on a.id=b.detail WHERE '
    sql += f"dp='{params.dp}' and " if params.dp else ''
    sql += f"b.uid='{params.uid}' and " if params.uid else ''
    sql += f"b.pay_date between '{params.start}' and '{params.end}' "
    order = f' order by {params.field} {params.order} ' if params.order and params.field else ' '
    sql += order if params.uid or params.single else f'group by b.detail{order}{params.limit} '
    return sql_translate(sql, 'dic_', ['sys_department', 'gs_station', 'gs_station', 'gs_station', 'gs_jgdm'],
                         ['dp', 'sf', 'zd', 'dcdd', 'jgdm'])


def sql_translate(sql, prefix, tables, fields):
    return f"select _t_.*,{','.join(f'_t_{i}.name {f}N' for i,f in enumerate(fields))} from ({sql}) _t_ {' '.join(f'left join {prefix}{tables[i]} _t_{i} on _t_.{f}=_t_{i}.id' for i,f in enumerate(fields))}"


@router.get("", response_model=ResponseModel)
async def get_details(_: IUser = role_verify(1), query: DataQuerySE = query(QueryType.SE)):
    """
    获取值乘详情数据
    """
    role_verify(1, 3, 4, 5)
    data = {'items': await db_pools.mysql.fetch_all(base_sql(query))}
    if not query.uid or query.page == 1:
        data.update({
            'total': (await db_pools.mysql.fetch_one(
                f"""SELECT count(*) c FROM (SELECT count(*) c FROM dat_gs_zc_detail a join dat_gs_zc b on a.id=b.detail WHERE{f"dp='{query.dp}' and" if query.dp else ''} b.pay_date between '{query.start}' and '{query.end}' GROUP BY b.detail) c"""
            ))['c']
        })
    return {'detail': data}


# @router.get("/download")
# async def get_details(user: IUser = role_verify(3), params: dict = Depends(get_params)):
#     params['c'] = ''
#     columns = ['报单编号', '报单日期', '部门', '工资号', '人员', '机车型号', '机车编号', '车次', '记工码', '记工代码', '始发站', '终到站',
#                '出勤时间', '接车时间', '出段时间', '开车时间', '到达时间', '入段时间', '交车时间', '退勤时间', '调车地点', '调车地点代码', '劳动工时', '走行公里']
#     if params['p'] or params['single']:
#         columns.insert(4, '位次')
#     d = pd.DataFrame(dict(x) for x in await db_pools.mysql.fetch_all(base_sql(params)))
#     d.columns = columns
#     return DataFrameResponse(d, '乘务员值乘记录详情表.xlsx')

# @router.put("", response_model=ResponseModel)
# async def put_details(
#         user: IUser = role_verify(3),
#         start: str = Body(...),
#         end: str = Body(...)):
#     return {'detail': {'action': 'sync_data', 'data': {'start': start, 'end': end}}}
