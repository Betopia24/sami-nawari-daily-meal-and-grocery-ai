from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.errors import AppError


async def app_error_handler(request: Request, exc: AppError):
    request_id=getattr(request.state,'request_id','unknown')
    return JSONResponse(status_code=exc.status_code,content={
        'request_id':request_id,
        'error':{'code':exc.code,'message':exc.message,'retryable':exc.retryable},
    })
