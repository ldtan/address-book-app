import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import settings
from core.logging import configure_logging

logger = logging.getLogger("address_book")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application lifespan starting")

    # Initialize database
    # Note: Explicitly import models to ensure they are registered with Base.metadata
    from infrastructure.database import init_db
    from modules.address import models  # noqa: F401

    logger.info("Initializing database")
    await init_db()
    logger.info("Database initialized")

    yield

    logger.info("Application lifespan shutting down")


def create_app() -> FastAPI:
    configure_logging(settings.LOG_LEVEL)
    logger.info("Creating FastAPI application")

    app = FastAPI(
        title="Address Book API",
        description="This is an Address Book API.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS configuration
    # Note: In production, you should specify allowed origins instead of using "*"
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["*"],
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    #     allow_credentials=True,
    # )

    # Import and include your routers here
    from modules.address.routers import router as address_router

    app.include_router(address_router, prefix=settings.API_PREFIX)

    logger.info("FastAPI application initialized")
    return app


if __name__ == "__main__":
    import uvicorn

    if settings.DEBUG:
        reload_app = True
    else:
        reload_app = False

    uvicorn.run(
        "main:create_app",
        host="0.0.0.0",
        port=5000,
        reload=reload_app,
        factory=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
