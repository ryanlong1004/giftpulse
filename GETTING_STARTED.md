# GiftPulse - Twilio Log Monitor

## 🎉 Project Status: Core Infrastructure Complete!

The GiftPulse Twilio Log Monitor has been successfully built out with all core Phase 1 & 2 components from the project plan.

## ✅ What's Been Implemented

### 1. **Project Setup** ✓

- Complete directory structure following best practices
- Python dependencies configured in `requirements.txt`
- Environment configuration with `.env.example`
- Git repository initialized with proper `.gitignore`
- Comprehensive `README.md` documentation

### 2. **Database Layer** ✓

- SQLAlchemy models for all entities:
  - `Log` - Stores Twilio logs (calls, messages, alerts)
  - `MonitoringRule` - Configurable pattern matching rules
  - `Action` - Actions to execute when patterns match
  - `AlertHistory` - Tracks triggered alerts
- Alembic configured for database migrations
- Database connection manager with session handling
- Support for PostgreSQL with JSONB for flexible data storage

### 3. **Twilio Integration** ✓

- `TwilioClientWrapper` class for API interactions
- Methods to fetch:
  - Call logs
  - Message logs
  - Monitor alerts
- Pagination handling for large datasets
- Error handling with retries
- Singleton pattern for efficient resource usage

### 4. **Log Fetcher Service** ✓

- `LogFetcherService` for polling Twilio API
- Automatic deduplication using `twilio_sid`
- Stores logs with full metadata
- Marks logs for processing pipeline
- Incremental fetching (only new logs)

### 5. **Pattern Matching Engine** ✓

- `PatternMatcher` with support for:
  - **Error Code Matching** - Match specific Twilio error codes
  - **Regex Patterns** - Flexible text pattern matching
  - **Status Matching** - Filter by call/message status
  - **Threshold Detection** - Count-based alerts (e.g., 10 errors in 5 min)
- Processes logs against all enabled rules
- Triggers appropriate actions when patterns match

### 6. **Action Handler System** ✓

- Base action handler interface
- **Email Action Handler**:
  - SMTP support with TLS
  - Jinja2 template rendering
  - Multiple recipients
  - Custom subjects and bodies
- **Webhook Action Handler**:
  - HTTP POST/PUT support
  - Custom headers and payload
  - Retry logic with configurable attempts
  - Timeout handling
- Action execution tracking in `AlertHistory`

### 7. **Celery Task Queue** ✓

- Celery app configured with Redis backend
- **Periodic Task**: `poll_twilio_logs`
  - Runs every 5 minutes (configurable)
  - Fetches new logs from Twilio
  - Stores in database
- **Processing Task**: `process_unprocessed_logs`
  - Checks logs against monitoring rules
  - Executes matching actions
- Task scheduling with Celery Beat

### 8. **REST API** ✓

- FastAPI application with:
  - **Log Endpoints**:
    - `GET /api/logs` - List logs with pagination and filtering
    - `GET /api/logs/{id}` - Get specific log details
  - **Rule Endpoints**:
    - `GET /api/rules` - List all monitoring rules
    - `POST /api/rules` - Create new rule
    - `PUT /api/rules/{id}` - Update rule
    - `DELETE /api/rules/{id}` - Delete rule
  - **Action Endpoints**:
    - `GET /api/actions` - List all actions
    - `POST /api/actions` - Create action
    - `PUT /api/actions/{id}` - Update action
    - `DELETE /api/actions/{id}` - Delete action
  - **Alert Endpoints**:
    - `GET /api/alerts` - View alert history with pagination
  - `GET /api/health` - Health check endpoint
- Pydantic schemas for request/response validation
- OpenAPI/Swagger documentation at `/docs`
- CORS middleware configured
- Request logging middleware

### 9. **Docker Infrastructure** ✓

- **Dockerfile** for application container
- **docker-compose.yml** with services:
  - PostgreSQL database
  - Redis for task queue
  - API service (FastAPI)
  - Celery worker
  - Celery beat scheduler
- Health checks for all services
- Volume mounts for development
- Network configuration

### 10. **Utilities & Helpers** ✓

- Structured JSON logging
- Helper functions:
  - Error code parsing
  - Time window checking
  - Phone number sanitization
  - Safe dictionary access
  - Duration formatting
- Configuration management with Pydantic Settings

## 🚀 Quick Start Guide

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Or use Docker (recommended)
docker-compose up -d
```

### Configuration

1. **Copy environment template**:

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   DATABASE_URL=postgresql://user:pass@localhost:5432/giftpulse_monitor
   SMTP_HOST=smtp.gmail.com
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_password
   ```

### Running the Application

#### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Option 2: Local Development

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 3: Start Celery Beat
celery -A app.tasks.celery_app beat --loglevel=info

# Terminal 4: Start API
uvicorn app.api.main:app --reload
```

### Database Setup

```bash
# Run migrations
alembic upgrade head

# Seed with example data (optional)
python scripts/seed_data.py
```

### Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📝 Usage Examples

### Create a Monitoring Rule

```bash
curl -X POST http://localhost:8000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Failed Call Detection",
    "description": "Alert on failed calls",
    "enabled": true,
    "log_type": "call",
    "pattern_type": "error_code",
    "pattern_value": "30001,30002,30003"
  }'
```

### Create an Email Action

```bash
curl -X POST http://localhost:8000/api/actions \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": "<rule-uuid>",
    "action_type": "email",
    "config": {
      "recipients": ["ops@example.com"],
      "subject": "Twilio Alert",
      "body": "Error {{ error_code }} detected"
    },
    "enabled": true
  }'
```

### Query Recent Logs

```bash
# Get recent logs
curl http://localhost:8000/api/logs?page=1&page_size=20

# Filter unprocessed logs
curl http://localhost:8000/api/logs?processed=false
```

### View Alert History

```bash
curl http://localhost:8000/api/alerts?page=1&page_size=50
```

## 🏗️ Architecture Overview

```
┌─────────────────┐
│  Twilio API     │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  GiftPulse Monitor                  │
│  ┌──────────────────────────────┐  │
│  │  Celery Beat (Scheduler)     │  │
│  │  - Triggers polling every 5m │  │
│  └─────────────┬────────────────┘  │
│                ↓                    │
│  ┌──────────────────────────────┐  │
│  │  Celery Worker               │  │
│  │  - Fetches Twilio logs       │  │
│  │  - Stores in database        │  │
│  │  - Triggers pattern matching │  │
│  └─────────────┬────────────────┘  │
│                ↓                    │
│  ┌──────────────────────────────┐  │
│  │  Pattern Matcher             │  │
│  │  - Checks logs vs rules      │  │
│  │  - Triggers actions          │  │
│  └─────────────┬────────────────┘  │
│                ↓                    │
│  ┌──────────────────────────────┐  │
│  │  Action Handlers             │  │
│  │  - Email notifications       │  │
│  │  - Webhook triggers          │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  FastAPI REST API            │  │
│  │  - Manage rules & actions    │  │
│  │  - Query logs & alerts       │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
         │              │
         ↓              ↓
   ┌──────────┐   ┌─────────┐
   │PostgreSQL│   │  Redis  │
   └──────────┘   └─────────┘
```

## 📊 Database Schema

See `PROJECT_PLAN.md` for detailed schema documentation.

Key tables:

- `logs` - Twilio log storage
- `monitoring_rules` - Pattern matching configuration
- `actions` - Action definitions
- `alert_history` - Execution tracking

## 🔧 Configuration Options

All configuration is via environment variables. Key settings:

- `POLL_INTERVAL_SECONDS` - How often to poll Twilio (default: 300)
- `WEBHOOK_TIMEOUT_SECONDS` - Webhook timeout (default: 30)
- `WEBHOOK_RETRY_ATTEMPTS` - Retry attempts (default: 3)
- `LOG_LEVEL` - Logging verbosity (default: INFO)

See `.env.example` for complete list.

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

## 📚 Next Steps

### Immediate (Ready to Use):

1. Configure your Twilio credentials in `.env`
2. Start the services with `docker-compose up`
3. Create monitoring rules via API
4. Watch logs being processed automatically!

### Future Enhancements (From PROJECT_PLAN.md):

- Web dashboard for visual monitoring
- SMS notifications via Twilio
- Slack integration
- Machine learning for anomaly detection
- Multi-account support
- Plugin system for custom handlers
- Real-time WebSocket streaming
- Historical analytics and reporting

## 🐛 Troubleshooting

### Logs not appearing

- Check Twilio credentials in `.env`
- Verify Celery worker is running: `docker-compose logs celery-worker`
- Check Celery beat scheduler: `docker-compose logs celery-beat`

### Email not sending

- Verify SMTP configuration
- Check for 2FA/app-specific password requirements
- Review application logs for SMTP errors

### Database connection errors

- Ensure PostgreSQL is running
- Verify `DATABASE_URL` in `.env`
- Check network connectivity in Docker

## 📄 License

[Specify your license]

## 👥 Contributors

Built following the comprehensive plan in `PROJECT_PLAN.md`.

---

**Status**: ✅ Phase 1 & 2 Complete - Ready for Testing and Deployment!
