"""API route handlers"""
from fastapi import APIRouter, HTTPException, status
from app.models import (
    AngleRequest,
    RotateRequest,
    CompartmentRequest,
    ServoResponse,
    HealthResponse
)
from app.dependencies import get_servo_controller
from app.config import settings

router = APIRouter()


@router.get("/", tags=["Info"])
async def root():
    """Get API information and available endpoints"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "servo_angle": "/servo/angle",
            "servo_rotate": "/servo/rotate",
            "servo_compartments": "/servo/compartments",
            "servo_reset": "/servo/reset"
        }
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API and servo health status"""
    return HealthResponse(
        status="healthy",
        servo="connected",
        pin=settings.servo_pin
    )


@router.post(
    "/servo/angle",
    response_model=ServoResponse,
    status_code=status.HTTP_200_OK,
    tags=["Servo Control"]
)
async def set_servo_angle(request: AngleRequest):
    """
    Set servo to a specific angle (0-180 degrees)
    
    - **angle**: Target angle in degrees (0-180)
    - **speed**: Movement speed (0.1=fast, 5.0=slow)
    """
    try:
        servo = get_servo_controller()
        servo.set_angle(request.angle, request.speed)
        
        return ServoResponse(
            status="success",
            message=f"Servo moved to {request.angle}°",
            data={"angle": request.angle, "speed": request.speed}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set servo angle: {str(e)}"
        )


@router.post(
    "/servo/rotate",
    response_model=ServoResponse,
    status_code=status.HTTP_200_OK,
    tags=["Servo Control"]
)
async def rotate_servo(request: RotateRequest):
    """
    Rotate servo by relative degrees
    
    - **degrees**: Degrees to rotate (-360 to 360)
    - **speed**: Movement speed
    """
    try:
        servo = get_servo_controller()
        servo.rotate_degrees(request.degrees, request.speed)
        
        return ServoResponse(
            status="success",
            message=f"Servo rotated {request.degrees}°",
            data={"degrees": request.degrees, "speed": request.speed}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rotate servo: {str(e)}"
        )


@router.post(
    "/servo/compartments",
    response_model=ServoResponse,
    status_code=status.HTTP_200_OK,
    tags=["Servo Control"]
)
async def advance_compartments(request: CompartmentRequest):
    """
    Advance through compartments (e.g., for fish feeder)
    
    - **compartments**: Number of compartments to advance (1-50)
    - **speed**: Movement speed
    """
    try:
        servo = get_servo_controller()
        servo.spin_compartments(request.compartments, request.speed)
        
        return ServoResponse(
            status="success",
            message=f"Advanced {request.compartments} compartment(s)",
            data={"compartments": request.compartments, "speed": request.speed}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to advance compartments: {str(e)}"
        )


@router.post(
    "/servo/reset",
    response_model=ServoResponse,
    status_code=status.HTTP_200_OK,
    tags=["Servo Control"]
)
async def reset_servo():
    """Reset servo to neutral position (90 degrees)"""
    try:
        servo = get_servo_controller()
        servo.reset()
        
        return ServoResponse(
            status="success",
            message="Servo reset to neutral position (90°)",
            data={"angle": 90}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset servo: {str(e)}"
        )

