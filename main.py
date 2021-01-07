import os

from uvicorn import run
from fastapi import FastAPI

from utils.db_pools import db_pools


app = FastAPI(
    title="ZJD_LZXT",
    version="1.0.0",
    description="株洲机务段劳资信息管理系统"
)


@app.on_event("startup")
async def startup():
    await db_pools.init()


@app.on_event("shutdown")
async def shutdown():
    await db_pools.close()


for root, _, files in os.walk('./routers'):
    if os.path.basename(root) == '__pycache__':
        continue
    for file in files:
        n, e = os.path.splitext(file)
        if n == '__init__':
            continue
        if e == '.py':
            app.include_router(__import__(os.path.join(root[2:], n).replace('/', '.'), fromlist=(
                n,)).router, prefix=f"/api/{root[10:] if n == 'index' else os.path.join(root[10:], n)}")


if __name__ == "__main__":
    run('main:app', host='10.183.196.93',
        port=3333, log_level='info', reload=True)