"""FastAPI application factory and lifecycle management"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.servo import ServoController
from app.dependencies import set_servo_controller
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Handles startup and shutdown events for proper resource management.
    """
    # Startup: Initialize servo controller
    servo = ServoController(servo_pin=settings.servo_pin)
    servo.initialize()
    set_servo_controller(servo)

    yield

    # Shutdown: Clean up GPIO resources
    servo.cleanup()


def create_app() -> FastAPI:
    """
    Application factory

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Add CORS middleware (adjust origins as needed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router)

    return app


# Create the application instance
app = create_app()

