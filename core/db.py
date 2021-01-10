import typing

import aioredis
import pandas as pd
from databases import Database

from core.config import DB_MYSQL_CONFIG, DB_REDIS_CONFIG


class Database(Database):
    async def insert(self, table: str, row: dict, duplicate: bool = False):
        sql = f"""
                insert into {table}
                ({','.join(row.keys())})
                values ('{"','".join(row.values())}')
                """
        if duplicate:
            sql += f""" ON DUPLICATE KEY UPDATE
                        {','.join(f"{k}='{v}'" for k,v in row.items())}
                    """
        await self.execute(sql)


class DB:
    async def init(self):
        self.mysql = Database(**DB_MYSQL_CONFIG)
        await self.mysql.connect()
        self.redis = await aioredis.create_redis_pool(**DB_REDIS_CONFIG)

    async def close(self):
        await self.mysql.disconnect()
        await self.redis.close()


def to_df(data: typing.List[typing.Mapping]) -> pd.DataFrame:
    return pd.DataFrame(data, columns=data[0].keys() if isinstance(data, list) else data.keys())
