import os
import re

from fastapi import FastAPI

from core.config import BASE_CONFIG, ROUTER_PREFIX, ROUTERS_DIR
from core.db import DB


def get_default_app() -> FastAPI:
    app = FastAPI(**BASE_CONFIG)

    @app.on_event('startup')
    async def start_app() -> None:
        app.db = DB()
        await app.db.init()

    @app.on_event('shutdown')
    async def stop_app() -> None:
        await app.db.close()

    _init_routes(app)
    return app


def _init_routes(app: FastAPI):
    for root, _, files in os.walk(ROUTERS_DIR):
        if os.path.basename(root) == '__pycache__':
            continue
        for file in files:
            filename, suffix = os.path.splitext(file)
            if filename == '__init__':
                continue
            if suffix == '.py':
                root = re.sub(r'[\\/]', '.', root)
                router = __import__(f'{root}.{filename}', fromlist=(filename, )).router
                prefix = f"{ROUTER_PREFIX}{root[len(ROUTERS_DIR):]}"
                prefix += '' if filename == 'index' else f"/{filename}"
                app.include_router(router=router, prefix=prefix.replace('.', '/'))