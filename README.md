# GiftPulse - Twilio Log Monitor

A monitoring application that continuously monitors Twilio account logs, detects errors or specific log patterns, and takes automated actions such as sending email notifications or triggering webhooks.

## Features

- **Continuous Log Monitoring**: Automatically polls Twilio API for new logs at configurable intervals
- **Pattern Detection**: Identify errors, specific log messages, and threshold-based patterns
- **Automated Actions**: Send email notifications and trigger webhooks when patterns match
- **Flexible Configuration**: Easy-to-configure rules for pattern matching and actions
- **REST API**: Manage monitoring rules, actions, and query logs
- **Webhook Support**: Expose webhooks for external integrations
- **Background Processing**: Uses Celery for reliable background task execution

## Technology Stack

- **Backend**: Python with FastAPI
- **Task Queue**: Celery with Redis
- **Database**: PostgreSQL
- **Email**: SMTP/Async email support
- **Deployment**: Docker and Docker Compose

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis
- Twilio Account (Account SID and Auth Token)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd giftpulse
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up the database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   
   Start Redis (if not running):
   ```bash
   redis-server
   ```
   
   Start Celery worker:
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   ```
   
   Start Celery beat (scheduler):
   ```bash
   celery -A app.tasks.celery_app beat --loglevel=info
   ```
   
   Start API server:
   ```bash
   uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Docker Deployment

```bash
docker-compose up -d
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SMTP_*`: Email configuration
- `POLL_INTERVAL_SECONDS`: How often to poll Twilio (default: 300)

### Monitoring Rules

Create monitoring rules via the API to define what patterns to detect:

```bash
curl -X POST http://localhost:8000/api/rules \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "name": "Failed Call Detection",
    "description": "Alert when calls fail",
    "enabled": true,
    "log_type": "call",
    "pattern_type": "error_code",
    "pattern_value": "30001,30002,30003"
  }'
```

### Actions

Configure actions to execute when patterns match:

```bash
curl -X POST http://localhost:8000/api/actions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "rule_id": "rule-uuid-here",
    "action_type": "email",
    "config": {
      "recipients": ["ops@example.com"],
      "subject": "Twilio Alert",
      "template": "error_notification"
    },
    "enabled": true
  }'
```

## API Documentation

Once the application is running, visit:
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Key Endpoints

- `GET /api/health` - Health check
- `GET /api/logs` - Query logs
- `GET /api/rules` - List monitoring rules
- `POST /api/rules` - Create monitoring rule
- `GET /api/actions` - List actions
- `POST /api/actions` - Create action
- `GET /api/alerts` - View alert history

## Development

### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

### Code Formatting

```bash
black app tests
isort app tests
flake8 app tests
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Project Structure

```
giftpulse/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Core business logic
│   ├── actions/         # Action handlers
│   ├── api/             # FastAPI routes and schemas
│   ├── tasks/           # Celery tasks
│   └── utils/           # Utility functions
├── alembic/             # Database migrations
├── tests/               # Test suite
├── templates/           # Email templates
└── scripts/             # Utility scripts
```

## Monitoring

The application provides metrics compatible with Prometheus. Key metrics include:
- Log processing rate
- Pattern match rate
- Action success/failure rate
- API response times

## Troubleshooting

### Logs not appearing

1. Check Twilio credentials in `.env`
2. Verify Celery worker is running
3. Check logs: `docker-compose logs -f celery-worker`

### Email not sending

1. Verify SMTP configuration in `.env`
2. Check email action configuration
3. Review application logs for SMTP errors

### Database connection errors

1. Ensure PostgreSQL is running
2. Verify `DATABASE_URL` in `.env`
3. Check database permissions

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Run tests and linting
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub or contact [support email].

## Roadmap

See `PROJECT_PLAN.md` for detailed implementation plan and future enhancements.
