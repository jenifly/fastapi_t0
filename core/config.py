from sys import maxsize
from fastapi.responses import ORJSONResponse

# ======================= project configuration =======================
BASE_CONFIG = dict(
    title="Jy",
    version="0.0.1",
    description="",
    # docs_url=None,
    redoc_url=None,
    default_response_class=ORJSONResponse)

# ======================= router configuration =======================
ROUTERS_DIR = 'routers'
ROUTER_PREFIX = '/api'

#  ====================== security configuration =====================
SECRET_KEY = "f268fb9f508111eaaa87c75bfedfb617503e3a6126524682a5598d0c08ec1da1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 15

#  ====================== database configuration =====================
DB_MYSQL_CONFIG = dict(url='mysql://root:jy0.1@localhost/test', min_size=1, max_size=1)

DB_REDIS_CONFIG = dict(address='redis://localhost/1', minsize=1, maxsize=1)
