"""Servo controller hardware interface"""
import time
import threading
from typing import Optional
import RPi.GPIO as GPIO
from app.config import settings


class ServoController:
    """
    Thread-safe servo controller for Raspberry Pi

    Manages GPIO PWM signals to control a standard hobby servo motor.
    """

    def __init__(self, servo_pin: Optional[int] = None):
        """
        Initialize the servo controller

        Args:
            servo_pin: GPIO pin number (BCM mode). Defaults to settings.servo_pin
        """
        self.servo_pin = servo_pin or settings.servo_pin
        self.pwm: Optional[GPIO.PWM] = None
        self.lock = threading.Lock()
        self.current_angle = 90.0  # Track current position
        self._initialized = False

    def initialize(self) -> None:
        """Initialize GPIO and PWM"""
        if self._initialized:
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.servo_pin, settings.pwm_frequency)
        self.pwm.start(0)
        self._initialized = True

    def _angle_to_duty_cycle(self, angle: float) -> float:
        """
        Convert angle (0-180) to PWM duty cycle percentage

        Args:
            angle: Target angle in degrees

        Returns:
            Duty cycle percentage
        """
        duty_range = settings.max_duty_cycle - settings.min_duty_cycle
        return settings.min_duty_cycle + (angle / 180.0) * duty_range

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
            duty_cycle = self._angle_to_duty_cycle(angle)
            self.pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(speed)
            self.pwm.ChangeDutyCycle(0)  # Stop signal to prevent jitter
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
                duty_cycle = self._angle_to_duty_cycle(angle)
                self.pwm.ChangeDutyCycle(duty_cycle)
                time.sleep(speed)

            self.pwm.ChangeDutyCycle(0)

    def spin_compartments(self, compartments: int, speed: float = None) -> None:
        """
        Advance through compartments (e.g., fish feeder compartments)

        Uses incremental duty cycle changes to advance one compartment at a time.

        Args:
            compartments: Number of compartments to advance
            speed: Movement delay. Defaults to settings.default_speed
        """
        if speed is None:
            speed = settings.default_speed

        with self.lock:
            for i in range(compartments):
                position = settings.compartment_initial_position + (
                    settings.compartment_increment * i
                )
                self.pwm.ChangeDutyCycle(position)
                time.sleep(speed)
                self.pwm.ChangeDutyCycle(0)
                time.sleep(settings.compartment_delay)

    def reset(self) -> None:
        """Reset servo to neutral position (90 degrees)"""
        self.set_angle(90.0)

    def cleanup(self) -> None:
        """Clean up GPIO resources"""
        if self._initialized and self.pwm:
            self.pwm.stop()
            GPIO.cleanup()
            self._initialized = False

    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

