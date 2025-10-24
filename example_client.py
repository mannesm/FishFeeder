"""
Example usage of the Fish Feeder API

This script demonstrates how to interact with the API programmatically.
"""
import requests
from time import sleep

# Base URL of the API (adjust if running remotely)
BASE_URL = "http://localhost:8000"


def check_health():
    """Check if the API is healthy"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.json()}")
    return response.status_code == 200


def set_angle(angle: float, speed: float = 0.5):
    """Set servo to specific angle"""
    response = requests.post(
        f"{BASE_URL}/servo/angle",
        json={"angle": angle, "speed": speed}
    )
    print(f"Set Angle: {response.json()}")
    return response.json()


def rotate_degrees(degrees: float, speed: float = 0.5):
    """Rotate servo by degrees"""
    response = requests.post(
        f"{BASE_URL}/servo/rotate",
        json={"degrees": degrees, "speed": speed}
    )
    print(f"Rotate: {response.json()}")
    return response.json()


def feed_fish(compartments: int = 1, speed: float = 0.5):
    """Advance compartments (feed fish)"""
    response = requests.post(
        f"{BASE_URL}/servo/compartments",
        json={"compartments": compartments, "speed": speed}
    )
    print(f"Feed Fish: {response.json()}")
    return response.json()


def reset_servo():
    """Reset servo to neutral position"""
    response = requests.post(f"{BASE_URL}/servo/reset")
    print(f"Reset: {response.json()}")
    return response.json()


if __name__ == "__main__":
    print("🐟 Fish Feeder API Client Example\n")

    # Check health
    if not check_health():
        print("❌ API is not healthy!")
        exit(1)

    print("\n" + "="*50 + "\n")

    # Example 1: Set to specific angle
    print("Example 1: Moving to 45 degrees")
    set_angle(45, speed=1.0)
    sleep(2)

    print("\n" + "="*50 + "\n")

    # Example 2: Rotate by degrees
    print("Example 2: Rotating 90 degrees")
    rotate_degrees(90, speed=1.0)
    sleep(2)

    print("\n" + "="*50 + "\n")

    # Example 3: Feed fish (advance 1 compartment)
    print("Example 3: Feeding fish (1 compartment)")
    feed_fish(compartments=1, speed=0.5)
    sleep(2)

    print("\n" + "="*50 + "\n")

    # Example 4: Reset
    print("Example 4: Resetting to neutral position")
    reset_servo()

    print("\n✅ All examples completed!")

