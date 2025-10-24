from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

servo_pin = 17

# Use PiGPIOFactory for better PWM control (falls back to default if pigpio not available)
try:
    factory = PiGPIOFactory()
except:
    factory = None  # Use default pin factory

# Initialize servo with min/max pulse widths for standard hobby servos
servo = Servo(
    servo_pin,
    min_pulse_width=0.5/1000,  # 0.5ms = 0°
    max_pulse_width=2.5/1000,   # 2.5ms = 180°
    pin_factory=factory
)

# Servo settings
initial_position = 0  # Neutral duty cycle (will be converted to angle)
increment = 1.3        # Increment duty cycle per compartment
compartments = 10       # Number of compartments in your feeder
current_compartment = 0

def duty_to_angle(duty_cycle):
    """Convert duty cycle percentage to angle (0-180)"""
    # Standard servos: 2.5% duty = 0°, 12.5% duty = 180°
    return min(180, max(0, (duty_cycle / 12.5) * 180.0))

def angle_to_value(angle):
    """Convert angle (0-180) to gpiozero value (-1 to 1)"""
    return (angle - 90.0) / 90.0

try:
    while True:
        # Calculate next position
        position = initial_position + (increment * current_compartment)

        # Convert duty cycle to angle, then to servo value
        angle = duty_to_angle(position)
        value = angle_to_value(angle)

        # Move servo to position
        servo.value = value
        print(f"Moved to compartment {current_compartment + 1} (Duty cycle: {position:.2f}%, Angle: {angle:.1f}°)")

        # Wait to allow servo to move fully
        time.sleep(2)

        # Detach servo to avoid jitter
        servo.value = None

        # Wait some time between feedings (e.g., every 5 seconds)
        time.sleep(2)

        # Move to next compartment (reset if full cycle completed)
        current_compartment = (current_compartment + 1) % compartments

except KeyboardInterrupt:
    print("Exiting...")

finally:
    servo.close()
