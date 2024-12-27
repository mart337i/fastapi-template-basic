from fastapi import FastAPI, HTTPException, Depends, Request
from base.logger import logger as _logger

async def log_request_info(request: Request):
    _logger.debug(
        f"{request.method} request to {request.url} metadata\n"
        f"\tHeaders: {request.headers}\n"
        f"\tPath Params: {request.path_params}\n"
        f"\tQuery Params: {request.query_params}\n"
        f"\tCookies: {request.cookies}\n"
    )