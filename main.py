from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time
import threading
from contextlib import asynccontextmanager

# Global servo controller instance
servo_controller = None


class ServoController:
    def __init__(self, servo_pin=17):
        self.servo_pin = servo_pin
        self.servo = None
        self.lock = threading.Lock()
        self.initialize()

    def initialize(self):
        """Initialize servo using gpiozero"""
        # Use PiGPIOFactory for better PWM control (falls back to default if pigpio not available)
        try:
            factory = PiGPIOFactory()
        except:
            factory = None  # Use default pin factory

        # Initialize servo with min/max pulse widths for standard hobby servos
        self.servo = Servo(
            self.servo_pin,
            min_pulse_width=0.5/1000,  # 0.5ms = 0°
            max_pulse_width=2.5/1000,   # 2.5ms = 180°
            pin_factory=factory
        )

    def _angle_to_value(self, angle: float) -> float:
        """Convert angle (0-180) to gpiozero value (-1 to 1)"""
        return (angle - 90.0) / 90.0

    def set_angle(self, angle: float, speed: float = 0.5):
        """
        Set servo to specific angle (0-180 degrees)
        Speed parameter controls delay between movements (higher = slower)
        """
        with self.lock:
            value = self._angle_to_value(angle)
            self.servo.value = value
            time.sleep(speed)

    def rotate_degrees(self, degrees: float, speed: float = 0.5):
        """
        Rotate servo by relative degrees from current position
        Note: Servos have limited range (typically 0-180°)
        """
        # For continuous rotation, we'll pulse the servo
        with self.lock:
            direction = 1 if degrees > 0 else -1
            steps = abs(int(degrees / 10))  # Break into 10-degree steps

            for _ in range(steps):
                angle = 90 + (direction * 45)  # 135° or 45° for direction
                value = self._angle_to_value(angle)
                self.servo.value = value
                time.sleep(speed)

            self.servo.value = 0  # Return to neutral

    def spin_compartments(self, compartments: int, speed: float = 0.5):
        """
        Spin through a specific number of compartments (like your original code)
        """
        with self.lock:
            initial_position = 0
            increment = 1.3

            for i in range(compartments):
                position = initial_position + (increment * i)
                # Convert duty cycle percentage to angle approximation
                angle = min(180, max(0, (position / 12.5) * 180.0))
                value = self._angle_to_value(angle)
                self.servo.value = value
                time.sleep(speed)
                self.servo.value = None  # Detach to reduce jitter
                time.sleep(0.2)

    def cleanup(self):
        """Clean up GPIO"""
        if self.servo:
            self.servo.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global servo_controller
    servo_controller = ServoController(servo_pin=17)
    yield
    # Shutdown
    servo_controller.cleanup()


app = FastAPI(
    title="Servo Controller API",
    description="Control your Raspberry Pi servo via REST API",
    version="1.0.0",
    lifespan=lifespan
)


# Pydantic models for request validation
class AngleRequest(BaseModel):
    angle: float = Field(..., ge=0, le=180, description="Target angle in degrees (0-180)")
    speed: float = Field(0.5, ge=0.1, le=5.0, description="Movement speed (0.1=fast, 5.0=slow)")


class RotateRequest(BaseModel):
    degrees: float = Field(..., ge=-360, le=360, description="Degrees to rotate (-360 to 360)")
    speed: float = Field(0.5, ge=0.1, le=5.0, description="Movement speed")


class CompartmentRequest(BaseModel):
    compartments: int = Field(..., ge=1, le=50, description="Number of compartments to advance")
    speed: float = Field(0.5, ge=0.1, le=5.0, description="Movement speed")


# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Servo Controller API is running",
        "endpoints": {
            "set_angle": "/servo/angle",
            "rotate": "/servo/rotate",
            "compartments": "/servo/compartments",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "servo": "connected"}


@app.post("/servo/angle")
async def set_angle(request: AngleRequest):
    """Set servo to a specific angle (0-180 degrees)"""
    try:
        servo_controller.set_angle(request.angle, request.speed)
        return {
            "status": "success",
            "message": f"Servo moved to {request.angle}°",
            "angle": request.angle
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/servo/rotate")
async def rotate(request: RotateRequest):
    """Rotate servo by relative degrees"""
    try:
        servo_controller.rotate_degrees(request.degrees, request.speed)
        return {
            "status": "success",
            "message": f"Servo rotated {request.degrees}°",
            "degrees": request.degrees
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/servo/compartments")
async def advance_compartments(request: CompartmentRequest):
    """Advance through compartments (like your fish feeder)"""
    try:
        servo_controller.spin_compartments(request.compartments, request.speed)
        return {
            "status": "success",
            "message": f"Advanced {request.compartments} compartments",
            "compartments": request.compartments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/servo/reset")
async def reset_servo():
    """Reset servo to neutral position (90 degrees)"""
    try:
        servo_controller.set_angle(90, 0.5)
        return {
            "status": "success",
            "message": "Servo reset to neutral position (90°)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

