"""Dependency injection for the application"""
from typing import Optional
from app.servo import ServoController

# Global servo controller instance
_servo_controller: Optional[ServoController] = None


def get_servo_controller() -> ServoController:
    """
    Get the global servo controller instance

    Returns:
        ServoController instance

    Raises:
        RuntimeError: If servo controller is not initialized
    """
    if _servo_controller is None:
        raise RuntimeError("Servo controller not initialized")
    return _servo_controller


def set_servo_controller(controller: ServoController) -> None:
    """
    Set the global servo controller instance

    Args:
        controller: ServoController instance to set
    """
    global _servo_controller
    _servo_controller = controller

