from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.public import router as public_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    docs_url=None if settings.is_production else "/docs",
    openapi_url=None if settings.is_production else "/openapi.json",
    redoc_url=None if settings.is_production else "/redoc",
    title="VOLUMA API",
    version="0.1.0",
)
app.include_router(health_router, prefix="/api")
app.include_router(public_router, prefix="/api/v1/public")
