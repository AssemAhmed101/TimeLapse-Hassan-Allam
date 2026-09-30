from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.core.config import cors_origins, settings, trusted_hosts
from app.core.logging import configure_logging
from app.services.storage_service import storage_service
from app.tasks.snapshot_scheduler import (
    start_snapshot_scheduler,
    stop_snapshot_scheduler,
)

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage_service.ensure_structure()
    start_snapshot_scheduler()
    yield
    stop_snapshot_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=trusted_hosts(),
)

app.include_router(api_router, prefix="/api/v1")
