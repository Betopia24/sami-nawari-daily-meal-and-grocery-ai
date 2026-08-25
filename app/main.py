from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.middleware import RequestContextMiddleware
from app.api.error_handlers import app_error_handler
from app.api.v1.router import router as v1_router
from app.container import build_production_container
from app.core.config import get_settings, Settings
from app.core.errors import AppError
from app.core.logging import configure_logging


def create_app(container=None, settings: Settings | None = None) -> FastAPI:
    settings=settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if app.state.container is None:
            app.state.container=build_production_container(settings)
        yield
        await app.state.container.close()

    app=FastAPI(title=settings.app_name,version=settings.app_version,docs_url=None if settings.is_production else '/docs',redoc_url=None)
    app.state.container=container
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(AppError,app_error_handler)
    app.include_router(v1_router)

    @app.get('/health/live')
    async def live(): return {'status':'ok'}

    @app.get('/health/ready')
    async def ready():
        c=app.state.container
        checks={'cache':await c.cache.ping(),'database':await c.health_repo.ping()}
        return {'status':'ok' if all(checks.values()) else 'degraded','checks':checks}

    app.router.lifespan_context=lifespan
    return app


app=create_app()
