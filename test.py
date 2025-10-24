import RPi.GPIO as GPIO
import time

servo_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # 50Hz PWM
pwm.start(0.0)  # Start all the way to the left to allow servo to have max range

# Servo settings
initial_position = 0  # Neutral duty cycle
increment = 1.3        # Increment duty cycle per compartment
compartments = 10       # Number of compartments in your feeder
current_compartment = 0

try:
    while True:
        # Calculate next position
        position = initial_position + (increment * current_compartment)

        # Move servo to position
        pwm.ChangeDutyCycle(position)
        print(f"Moved to compartment {current_compartment + 1} (Duty cycle: {position:.2f}%)")

        # Wait to allow servo to move fully
        time.sleep(2)

        # Turn off PWM signal to avoid jitter
        pwm.ChangeDutyCycle(0)

        # Wait some time between feedings (e.g., every 5 seconds)
        time.sleep(2)

        # Move to next compartment (reset if full cycle completed)
        current_compartment = (current_compartment + 1) % compartments

except KeyboardInterrupt:
    print("Exiting...")

finally:
    pwm.stop()
    GPIO.cleanup()
