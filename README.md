# Fish Feeder Servo Controller API

A FastAPI-based REST API to control a servo motor on Raspberry Pi, dockerized for easy deployment.

## Features

- 🎯 Set servo to specific angles (0-180°)
- 🔄 Rotate servo by relative degrees
- 🐟 Advance through compartments (for fish feeder)
- 🔒 Thread-safe operations
- 🐳 Fully dockerized
- ✅ Request validation with Pydantic
- 🏗️ Clean, modular architecture
- ⚙️ Environment-based configuration

## Project Structure

```
FishFeeder/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application factory
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   ├── servo.py             # Servo controller logic
│   ├── dependencies.py      # Dependency injection
│   └── api/
│       ├── __init__.py
│       └── routes.py        # API endpoints
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example            # Example environment variables
└── README.md
```

## Quick Start

### 1. Build and Run with Docker Compose (Recommended)

```bash
# Clone/navigate to the project
cd FishFeeder

# (Optional) Copy and customize environment variables
cp .env.example .env

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Or Run Locally (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

Configuration can be done via environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVO_PIN` | 17 | GPIO pin number (BCM mode) |
| `PWM_FREQUENCY` | 50 | PWM frequency in Hz |
| `DEFAULT_SPEED` | 0.5 | Default movement speed |
| `MIN_SPEED` | 0.1 | Minimum speed (fast) |
| `MAX_SPEED` | 5.0 | Maximum speed (slow) |
| `COMPARTMENT_INCREMENT` | 1.3 | Duty cycle increment per compartment |

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Set Angle (0-180 degrees)
```bash
curl -X POST http://localhost:8000/servo/angle \
  -H "Content-Type: application/json" \
  -d '{"angle": 90, "speed": 0.5}'
```

### Rotate by Degrees
```bash
curl -X POST http://localhost:8000/servo/rotate \
  -H "Content-Type: application/json" \
  -d '{"degrees": 45, "speed": 0.5}'
```

### Advance Compartments (Fish Feeder Mode)
```bash
curl -X POST http://localhost:8000/servo/compartments \
  -H "Content-Type: application/json" \
  -d '{"compartments": 3, "speed": 0.5}'
```

### Reset to Neutral (90°)
```bash
curl -X POST http://localhost:8000/servo/reset
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Adding New Endpoints

1. **Add models** in `app/models.py` for request/response validation
2. **Add route handlers** in `app/api/routes.py`
3. **Update servo logic** in `app/servo.py` if needed
4. The changes will be hot-reloaded automatically in development mode

## Development

### Running Tests (TODO)
```bash
pytest
```

### Code Quality
```bash
# Format code
black app/

# Lint
pylint app/

# Type checking
mypy app/
```

## Docker Commands

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

## Architecture Highlights

- **Separation of Concerns**: Configuration, models, business logic, and routes are separated
- **Dependency Injection**: Servo controller is injected as a dependency
- **Type Safety**: Full Pydantic validation and Python type hints
- **Resource Management**: Proper GPIO cleanup on shutdown
- **Thread Safety**: Locking mechanism for concurrent requests
- **CORS Enabled**: Can be called from web frontends

## Notes

- The servo won't spin infinitely because standard servos have a 0-180° range
- For continuous rotation, you'd need a continuous rotation servo
- The `speed` parameter adds delay to prevent jerky movements
- PWM signal is set to 0 between movements to prevent jitter

