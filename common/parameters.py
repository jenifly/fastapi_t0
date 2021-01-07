from fastapi import Depends


class SingleDotDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


def _params_base(uid: int = None,
                 dp: str = None,
                 page: int = 1,
                 pageSize: int = 20,
                 field: str = None,
                 order: str = None,
                 single: bool = None) -> dict:
    limit = f' limit {(page - 1) * pageSize},{pageSize}'
    return dict(uid=uid, dp=dp, limit=limit, field=field, order=order, single=single)


def params_se(start: str, end: str, params: dict = Depends(_params_base)) -> SingleDotDict:
    return SingleDotDict(dict(start=start, end=end, **params))


def params_ym(ym: int, params: dict = Depends(_params_base)) -> SingleDotDict:
    return SingleDotDict(dict(ym=ym, **params))
