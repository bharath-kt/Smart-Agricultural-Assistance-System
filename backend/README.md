# Smart Agriculture Platform - Backend

A production-ready FastAPI backend for a smart agriculture platform providing weather monitoring, market price prediction, plant disease detection, and government scheme information.

## Features

### 1. Weather Monitoring
- Real-time weather data from OpenWeatherMap API
- 7-day weather forecast
- Weather history storage in PostgreSQL
- Weather alerts for rain, drought, and high temperatures
- Redis caching for performance

### 2. Market Price Prediction
- Historical price data from Agmarknet
- ML-based price prediction using TensorFlow
- Price trends and analysis
- Support for multiple crops and locations

### 3. Plant Disease Detection
- CNN-based disease detection using PlantVillage dataset
- Image upload and processing with OpenCV
- Disease information and treatment recommendations
- Detection history tracking

### 4. Government Schemes
- Comprehensive scheme database (PM-KISAN, PMFBY, eNAM, etc.)
- Filter by state, farmer type, and crop
- Eligibility checking
- Search functionality

### 5. Authentication System
- Mobile number with OTP (Twilio integration)
- Mobile + password login
- Email registration with verification
- JWT tokens with refresh mechanism
- Rate limiting

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async SQLAlchemy)
- **Cache**: Redis
- **Task Queue**: Celery
- **ML**: TensorFlow, OpenCV
- **Container**: Docker, Docker Compose

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── weather.py
│   │           ├── market.py
│   │           ├── disease.py
│   │           └── schemes.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── db/
│   │   └── base.py
│   ├── models/
│   │   ├── user.py
│   │   ├── weather.py
│   │   ├── market.py
│   │   ├── disease.py
│   │   └── scheme.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── weather.py
│   │   ├── market.py
│   │   ├── disease.py
│   │   └── scheme.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── weather_service.py
│   │   ├── market_service.py
│   │   ├── disease_service.py
│   │   └── scheme_service.py
│   ├── tasks/
│   │   ├── celery_app.py
│   │   ├── weather_tasks.py
│   │   ├── market_tasks.py
│   │   └── notification_tasks.py
│   ├── utils/
│   │   └── cache.py
│   └── main.py
├── ml_models/
├── uploads/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start PostgreSQL and Redis**
```bash
# Using Docker
docker run -d -p 5432:5432 -e POSTGRES_DB=smart_agri -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run all services**
```bash
docker-compose up -d
```

2. **View logs**
```bash
docker-compose logs -f api
```

3. **Stop services**
```bash
docker-compose down
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/mobile` - Register with mobile
- `POST /api/v1/auth/register/email` - Register with email
- `POST /api/v1/auth/login/mobile-password` - Login with mobile + password
- `POST /api/v1/auth/login/email` - Login with email + password
- `POST /api/v1/auth/send-otp` - Send OTP
- `POST /api/v1/auth/verify-otp` - Verify OTP
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Weather
- `GET /api/v1/weather/current` - Current weather
- `GET /api/v1/weather/forecast` - 7-day forecast
- `GET /api/v1/weather/alerts` - Weather alerts

### Market
- `GET /api/v1/market/prices` - Historical prices
- `GET /api/v1/market/predict` - Price prediction
- `GET /api/v1/market/trends/{crop}` - Market trends
- `GET /api/v1/market/crops` - Available crops

### Disease Detection
- `POST /api/v1/disease/detect` - Detect disease from image
- `GET /api/v1/disease/info/{disease}` - Disease information
- `GET /api/v1/disease/history` - Detection history

### Government Schemes
- `GET /api/v1/schemes` - List schemes
- `GET /api/v1/schemes/{id}` - Scheme details
- `GET /api/v1/schemes/search` - Search schemes
- `POST /api/v1/schemes/eligibility` - Check eligibility

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgresql://postgres:password@localhost:5432/smart_agri |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `SECRET_KEY` | JWT secret key | - |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | - |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | - |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | - |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | - |
| `SMTP_HOST` | SMTP server host | smtp.gmail.com |
| `SMTP_USER` | SMTP username | - |
| `SMTP_PASSWORD` | SMTP password | - |

## API Documentation

When running in debug mode, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Celery Tasks

### Start Celery Worker
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

### Start Celery Beat (Scheduler)
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

## Testing

```bash
pytest
```

## Production Deployment

1. Update environment variables for production
2. Use a strong `SECRET_KEY`
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use a reverse proxy (nginx)
6. Monitor logs and set up alerts

## License

MIT License
