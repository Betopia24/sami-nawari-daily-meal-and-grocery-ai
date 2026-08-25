from uuid import UUID


def parse_user_id(value: str) -> UUID:
    return UUID(value)
