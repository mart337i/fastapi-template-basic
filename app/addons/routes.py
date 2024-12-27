from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
import starlette
import re

from base.logger import logger as _logger


router = APIRouter(
    prefix=f"/test",
    tags=["Test endpoint"],
)

dependency = []

@router.get("test/")
def test():
    return {"ok" : 200}