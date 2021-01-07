import aioredis
import pandas as pd

from databases import Database

from config import LZ_DB_MYSQL_CONFIG, LZ_DB_REDIS_CONFIG


class DBPools:
    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError

    async def init(self):
        self.mysql = Database(**LZ_DB_MYSQL_CONFIG)
        await self.mysql.connect()
        self.redis = await aioredis.create_redis_pool(**LZ_DB_REDIS_CONFIG)


    async def close(self):
        await self.mysql.disconnect()
        await self.redis.close()

def to_df(data):
    return pd.DataFrame(data, columns=data[0].keys() if isinstance(data, list) else data.keys())

db_pools = DBPools()

async def uinsert(_t, _k, _v):
    await db_pools.mysql.execute(f"""insert into {_t} ({','.join(_k)}) values ('{"','".join(_v)}') ON DUPLICATE KEY UPDATE {','.join(f"{_k[t]}='{_v[t]}'" for t in range(len(_k)))}""")