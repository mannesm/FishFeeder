"""Pydantic models for request/response validation"""
from pydantic import BaseModel, Field
from app.config import settings


class AngleRequest(BaseModel):
    """Request model for setting servo angle"""
    angle: float = Field(
        ...,
        ge=0,
        le=180,
        description="Target angle in degrees (0-180)",
        examples=[90, 45, 135]
    )
    speed: float = Field(
        default=settings.default_speed,
        ge=settings.min_speed,
        le=settings.max_speed,
        description="Movement speed (0.1=fast, 5.0=slow)"
    )


class RotateRequest(BaseModel):
    """Request model for rotating servo by degrees"""
    degrees: float = Field(
        ...,
        ge=-360,
        le=360,
        description="Degrees to rotate (-360 to 360)",
        examples=[45, -90, 180]
    )
    speed: float = Field(
        default=settings.default_speed,
        ge=settings.min_speed,
        le=settings.max_speed,
        description="Movement speed"
    )


class CompartmentRequest(BaseModel):
    """Request model for advancing compartments"""
    compartments: int = Field(
        ...,
        ge=1,
        le=50,
        description="Number of compartments to advance",
        examples=[1, 3, 5]
    )
    speed: float = Field(
        default=settings.default_speed,
        ge=settings.min_speed,
        le=settings.max_speed,
        description="Movement speed"
    )


class ServoResponse(BaseModel):
    """Standard response model for servo operations"""
    status: str = Field(description="Operation status", examples=["success"])
    message: str = Field(description="Human-readable message")
    data: dict | None = Field(default=None, description="Additional response data")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    servo: str
    pin: int

