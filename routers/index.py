from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from dependencies.db import DB, get_db

router = APIRouter()


@router.get('')
def test_get(db: get_db = Depends(get_db)):
    return db