from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    code: int = 4000
    result: Any


__RESPONSE_STATUS_MAP = {
    4000: 'success',
    4001: '您的账号已在其他设备登录，请确认账户安全，是否继续登录？',
}


def RESPONSE_CODE(code) -> dict:
    return {'code': code, 'result': __RESPONSE_STATUS_MAP[code]}


def RESPONSE_RESULT(result) -> dict:
    return {'code': 4000, 'result': result}
