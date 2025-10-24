from pydantic_settings import BaseSettings

"""Application configuration"""


class Config:
    env_file = ".env"
    case_sensitive = False



class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Fish Feeder Servo Controller"
    app_version: str = "1.0.0"
    app_description: str = "Control your Raspberry Pi servo via REST API"

    # Servo Settings
    servo_pin: int = 17


pwm_frequency: int = 50  # Hz

# Servo angle to duty cycle mapping
min_duty_cycle: float = 2.5  # 0 degrees
max_duty_cycle: float = 12.5  # 180 degrees

# Default speeds
default_speed: float = 0.5
min_speed: float = 0.1
max_speed: float = 5.0

# Compartment settings
compartment_initial_position: float = 0.0
compartment_increment: float = 1.3
compartment_delay: float = 0.2


settings = Settings()
