from dataclasses import dataclass


@dataclass(slots=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400
    retryable: bool = False

    def __str__(self) -> str:
        return self.message


class ResourceNotFound(AppError):
    def __init__(self, message: str = 'Resource not found') -> None:
        super().__init__('RESOURCE_NOT_FOUND', message, 404, False)


class ProfileNotFound(AppError):
    def __init__(self, message: str = 'AI profile not found') -> None:
        super().__init__('PROFILE_NOT_FOUND', message, 404, False)


class InsufficientProfileData(AppError):
    def __init__(self, message: str = 'Insufficient profile data') -> None:
        super().__init__('INSUFFICIENT_PROFILE_DATA', message, 422, False)


class NoCompatibleResults(AppError):
    def __init__(self, message: str = 'No compatible results found') -> None:
        super().__init__('NO_COMPATIBLE_RESULTS', message, 404, False)


class GenerationFailed(AppError):
    def __init__(self, message: str = 'AI generation failed', retryable: bool = True) -> None:
        super().__init__('AI_GENERATION_FAILED', message, 502, retryable)


class OutputValidationFailed(AppError):
    def __init__(self, message: str = 'AI output failed validation') -> None:
        super().__init__('AI_OUTPUT_VALIDATION_FAILED', message, 502, True)


class Forbidden(AppError):
    def __init__(self, message: str = 'Forbidden') -> None:
        super().__init__('FORBIDDEN', message, 403, False)


class RateLimited(AppError):
    def __init__(self, message: str = 'AI generation rate limit exceeded') -> None:
        super().__init__('RATE_LIMITED', message, 429, True)
