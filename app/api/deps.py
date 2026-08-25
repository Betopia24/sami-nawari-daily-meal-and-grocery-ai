from uuid import UUID
from fastapi import Depends, Header, Request, HTTPException
from app.core.security import ServiceAuthenticator


def get_container(request: Request):
    return request.app.state.container


def require_service_auth(
    request: Request,
    authorization: str | None = Header(default=None, alias='Authorization'),
):
    ServiceAuthenticator(request.app.state.container.settings).verify(authorization)


def get_user_id(
    _: None = Depends(require_service_auth),
    x_user_id: str = Header(alias='X-User-ID'),
) -> UUID:
    try:
        return UUID(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail='X-User-ID must be a UUID') from exc


def get_request_id(request: Request) -> str:
    return request.state.request_id
