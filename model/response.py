from typing import Any

from pydantic import BaseModel


RESPONSE_STATUS_MAP = {
    4000: "OK"
}

def RESPONSE_STATUS(status):
    return {"status": status, "detail": RESPONSE_STATUS_MAP[status]}

class ResponseModel(BaseModel):
    status: int = 4000
    detail: Any
