from pydantic import BaseModel


class IUser(BaseModel):
    uid: int = None
    name: str = None
    dp: str = None
    dpName: str = None
    pos: int = None
    posName: str = None
    role: int = None
    roleName: str = None


class IUserInDB(IUser):
    password: str


DICUSERINFO = dict()