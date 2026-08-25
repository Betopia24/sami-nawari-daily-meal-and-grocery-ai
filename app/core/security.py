import hmac
from fastapi import Header, HTTPException, status
from app.core.config import Settings


class ServiceAuthenticator:
    def __init__(self, settings: Settings) -> None:
        self._expected = settings.internal_service_token

    def verify(self, authorization: str | None) -> None:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing service token')
        supplied = authorization.removeprefix('Bearer ').strip()
        if not hmac.compare_digest(supplied, self._expected):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid service token')
