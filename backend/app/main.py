from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import auth_router as admin_auth_router
from app.api.admin import router as admin_router
from app.api.admin_editorial_content import router as admin_editorial_content_router
from app.api.admin_journal import router as admin_journal_router
from app.api.admin_projects import router as admin_projects_router
from app.api.admin_studio import router as admin_studio_router
from app.api.admin_taxonomies import router as admin_taxonomies_router
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
if not settings.is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_headers=["Content-Type", "X-VOLUMA-CSRF"],
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_origins=[settings.public_origin],
    )
app.include_router(health_router, prefix="/api")
app.include_router(public_router, prefix="/api/v1/public")
app.include_router(admin_auth_router, prefix="/api/v1/admin")
app.include_router(admin_router, prefix="/api/v1/admin")
app.include_router(admin_projects_router, prefix="/api/v1/admin")
app.include_router(admin_taxonomies_router, prefix="/api/v1/admin")
app.include_router(admin_editorial_content_router, prefix="/api/v1/admin")
app.include_router(admin_journal_router, prefix="/api/v1/admin")
app.include_router(admin_studio_router, prefix="/api/v1/admin")
