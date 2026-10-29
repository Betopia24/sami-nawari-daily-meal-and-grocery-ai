from re import fullmatch
from typing import TypeAlias
from uuid import UUID


UserId: TypeAlias = UUID | str


def parse_user_id(value: str) -> UserId:
    """Accept the UUIDs used by older clients and MongoDB ObjectIds."""
    try:
        return UUID(value)
    except ValueError:
        if fullmatch(r'[0-9a-fA-F]{24}', value):
            return value.lower()
        raise ValueError('user id must be a UUID or a 24-character MongoDB ObjectId')
