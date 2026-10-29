from fastapi import Header, Request, HTTPException
from app.core.ids import UserId, parse_user_id


def get_container(request: Request):
    return request.app.state.container


def get_user_id(
    x_user_id: str = Header(alias='X-User-ID'),
) -> UserId:
    try:
        return parse_user_id(x_user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail='X-User-ID must be a UUID or a 24-character MongoDB ObjectId',
        ) from exc


def get_request_id(request: Request) -> str:
    return request.state.request_id
