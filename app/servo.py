"""Servo controller hardware interface"""

import time
import threading
from typing import Optional
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from app.config import settings


class ServoController:
    """
    Thread-safe servo controller for Raspberry Pi

    Manages GPIO PWM signals to control a standard hobby servo motor using gpiozero.
    """

    def __init__(self, servo_pin: Optional[int] = None):
        """
        Initialize the servo controller

        Args:
            servo_pin: GPIO pin number (BCM mode). Defaults to settings.servo_pin
        """
        self.servo_pin = servo_pin or settings.servo_pin
        self.servo: Optional[Servo] = None
        self.lock = threading.Lock()
        self.current_angle = 90.0  # Track current position
        self._initialized = False

    def initialize(self) -> None:
        """Initialize GPIO and servo using gpiozero"""
        if self._initialized:
            return

        # Use PiGPIOFactory for better PWM control (falls back to default if pigpio not available)
        try:
            factory = PiGPIOFactory()
        except:
            factory = None  # Use default pin factory

        # Initialize servo with min/max pulse widths for standard hobby servos
        # min_pulse_width: 0.5ms (0°), max_pulse_width: 2.5ms (180°)
        self.servo = Servo(
            self.servo_pin,
            min_pulse_width=0.5/1000,  # 0.5ms
            max_pulse_width=2.5/1000,   # 2.5ms
            pin_factory=factory
        )
        self._initialized = True

    def _angle_to_value(self, angle: float) -> float:
        """
        Convert angle (0-180) to gpiozero servo value (-1 to 1)

        In gpiozero:
        -1 = minimum position (0°)
        0 = middle position (90°)
        1 = maximum position (180°)

        Args:
            angle: Target angle in degrees (0-180)

        Returns:
            Servo value between -1 and 1
        """
        # Convert 0-180 angle to -1 to 1 range
        return (angle - 90.0) / 90.0

    def set_angle(self, angle: float, speed: float = None) -> None:
        """
        Set servo to specific angle (0-180 degrees)

        Args:
            angle: Target angle in degrees (0-180)
            speed: Movement delay (higher = slower). Defaults to settings.default_speed
        """
        if speed is None:
            speed = settings.default_speed

        with self.lock:
            value = self._angle_to_value(angle)
            self.servo.value = value
            time.sleep(speed)
            # gpiozero keeps the position, no need to set to None
            self.current_angle = angle

    def rotate_degrees(self, degrees: float, speed: float = None) -> None:
        """
        Rotate servo by relative degrees from current position

        Note: Standard servos have limited range (0-180°)

        Args:
            degrees: Degrees to rotate (positive or negative)
            speed: Movement delay. Defaults to settings.default_speed
        """
        if speed is None:
            speed = settings.default_speed

        with self.lock:
            direction = 1 if degrees > 0 else -1
            steps = abs(int(degrees / 10))  # Break into 10-degree steps

            for _ in range(steps):
                # Pulse in the direction of rotation
                angle = 90 + (direction * 45)  # 135° or 45° for direction
                value = self._angle_to_value(angle)
                self.servo.value = value
                time.sleep(speed)

            # Return to neutral
            self.servo.value = 0

    def spin_compartments(self, compartments: int, speed: float = None) -> None:
        """
        Advance through compartments (e.g., fish feeder compartments)

        Uses incremental position changes to advance one compartment at a time.

        Args:
            compartments: Number of compartments to advance
            speed: Movement delay. Defaults to settings.default_speed
        """
        if speed is None:
            speed = settings.default_speed

        with self.lock:
            for i in range(compartments):
                # Convert the compartment position to an angle approximation
                # This assumes the compartment settings are designed for specific servo positions
                position = settings.compartment_initial_position + (
                    settings.compartment_increment * i
                )
                # Convert duty cycle percentage (0-100) to approximate angle
                # Standard servos: 2.5% duty = 0°, 12.5% duty = 180°
                # angle = (position - 2.5) * 180.0 / 10.0
                # For smoother compatibility, we'll use the position as a rough percentage
                # and map it to the servo value range
                angle = min(180, max(0, (position / 12.5) * 180.0))
                value = self._angle_to_value(angle)
                self.servo.value = value
                time.sleep(speed)
                # Detach briefly to reduce power/jitter
                self.servo.value = None
                time.sleep(settings.compartment_delay)

    def reset(self) -> None:
        """Reset servo to neutral position (90 degrees)"""
        self.set_angle(90.0)

    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        if self._initialized and self.servo:
            self.servo.close()
            self._initialized = False

    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
