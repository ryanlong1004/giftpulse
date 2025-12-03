# GiftPulse - Twilio Log Monitor - Project Plan

## Project Overview

GiftPulse is a monitoring application that continuously monitors Twilio account logs for the Gifthub application, detects errors or specific log patterns, and takes automated actions such as sending email notifications or triggering webhooks.

## Core Features

1. **Log Monitoring**: Continuously poll Twilio API for new logs
2. **Pattern Detection**: Identify errors and specific log messages
3. **Action System**: Execute actions (emails, webhooks) when patterns match
4. **Configuration**: Flexible configuration for patterns and actions
5. **Webhook Publishing**: Expose webhooks for external integrations
6. **Dashboard**: View log status and monitoring activity

## Technology Stack

- **Backend**: Python (Flask/FastAPI)
- **Task Queue**: Celery with Redis for background log polling
- **Database**: PostgreSQL for storing log history and configuration
- **Email**: SMTP or SendGrid for email notifications
- **Deployment**: Docker + Docker Compose

## Architecture Components

### 1. Log Fetcher Service

- Polls Twilio API at configurable intervals
- Fetches logs (calls, messages, errors, warnings, debugs)
- Stores new logs in database
- Triggers pattern matching engine

### 2. Pattern Matching Engine

- Configurable rules for log pattern detection
- Support for:
  - Error code matching
  - Message content pattern matching (regex)
  - Status code filtering
  - Time-based thresholds (e.g., 5 errors in 10 minutes)

### 3. Action Handler

- Execute actions when patterns match:
  - Send email notifications
  - Trigger outbound webhooks
  - Log to external services
  - Create incident tickets

### 4. API Service

- REST API for configuration management
- Webhook endpoints for external integrations
- Health check endpoints
- Log query interface

### 5. Web Dashboard (Optional Phase 2)

- View recent logs
- Configure monitoring rules
- Test actions
- View alert history

## Database Schema

### Tables

#### `logs`

```sql
- id (UUID, PK)
- twilio_sid (string, unique)
- log_type (enum: call, message, error, warning, debug)
- timestamp (datetime)
- status (string)
- error_code (string, nullable)
- error_message (text, nullable)
- from_number (string, nullable)
- to_number (string, nullable)
- raw_data (jsonb)
- processed (boolean)
- created_at (datetime)
```

#### `monitoring_rules`

```sql
- id (UUID, PK)
- name (string)
- description (text)
- enabled (boolean)
- log_type (enum)
- pattern_type (enum: error_code, regex, status, threshold)
- pattern_value (text)
- threshold_count (int, nullable)
- threshold_window_minutes (int, nullable)
- created_at (datetime)
- updated_at (datetime)
```

#### `actions`

```sql
- id (UUID, PK)
- rule_id (UUID, FK)
- action_type (enum: email, webhook, log)
- config (jsonb) -- email addresses, webhook URLs, etc.
- enabled (boolean)
- created_at (datetime)
```

#### `alert_history`

```sql
- id (UUID, PK)
- rule_id (UUID, FK)
- log_id (UUID, FK)
- action_id (UUID, FK)
- triggered_at (datetime)
- action_result (jsonb)
- success (boolean)
```

## Implementation Steps

### Phase 1: Core Infrastructure (Steps 1-5)

#### Step 1: Project Setup

- [ ] Create project directory structure
- [ ] Initialize Python virtual environment
- [ ] Create `requirements.txt` with dependencies:
  - Flask or FastAPI
  - Celery
  - Redis
  - PostgreSQL driver (psycopg2)
  - Twilio SDK
  - SQLAlchemy
  - Alembic (migrations)
  - python-dotenv
  - requests
- [ ] Create `.env.example` for configuration
- [ ] Create `.gitignore`
- [ ] Initialize git repository
- [ ] Create `README.md`

#### Step 2: Database Setup

- [ ] Create database models using SQLAlchemy
- [ ] Set up Alembic for migrations
- [ ] Create initial migration with all tables
- [ ] Create database connection manager
- [ ] Write seed data scripts for testing

#### Step 3: Twilio Integration

- [ ] Create Twilio client wrapper class
- [ ] Implement log fetching methods:
  - Fetch call logs
  - Fetch message logs
  - Fetch error logs
  - Fetch warning logs
- [ ] Add pagination handling for large log sets
- [ ] Implement incremental fetching (only new logs)
- [ ] Add error handling and retry logic
- [ ] Create unit tests for Twilio integration

#### Step 4: Log Fetcher Service

- [ ] Create Celery app configuration
- [ ] Implement periodic task for log polling
- [ ] Add logic to store logs in database
- [ ] Implement deduplication (check twilio_sid)
- [ ] Add logging and monitoring
- [ ] Configure task scheduling (e.g., every 1-5 minutes)
- [ ] Test with Docker Compose (Celery + Redis + PostgreSQL)

#### Step 5: Pattern Matching Engine

- [ ] Create base pattern matcher class
- [ ] Implement error code matcher
- [ ] Implement regex pattern matcher
- [ ] Implement status code matcher
- [ ] Implement threshold-based matcher (count in time window)
- [ ] Create pattern evaluation pipeline
- [ ] Add unit tests for each matcher type
- [ ] Integrate with log fetcher service

### Phase 2: Action System (Steps 6-8)

#### Step 6: Action Handler Framework

- [ ] Create base action handler interface
- [ ] Implement action registry system
- [ ] Add action execution queue
- [ ] Implement retry logic for failed actions
- [ ] Add action result tracking
- [ ] Create unit tests for action framework

#### Step 7: Email Action Handler

- [ ] Implement SMTP email sender
- [ ] Create email templates:
  - Error notification template
  - Summary report template
  - Custom alert template
- [ ] Add template variable substitution
- [ ] Support multiple recipients
- [ ] Add rate limiting (avoid spam)
- [ ] Test email delivery

#### Step 8: Webhook Action Handler

- [ ] Implement HTTP webhook caller
- [ ] Support multiple HTTP methods (POST, PUT)
- [ ] Add custom headers support
- [ ] Implement payload formatting (JSON)
- [ ] Add webhook retry logic
- [ ] Add timeout handling
- [ ] Test with mock webhook endpoints

### Phase 3: API & Configuration (Steps 9-11)

#### Step 9: REST API Development

- [ ] Set up Flask/FastAPI application
- [ ] Create API endpoints:
  - `GET /api/logs` - Query logs
  - `GET /api/logs/{id}` - Get specific log
  - `GET /api/rules` - List monitoring rules
  - `POST /api/rules` - Create monitoring rule
  - `PUT /api/rules/{id}` - Update rule
  - `DELETE /api/rules/{id}` - Delete rule
  - `GET /api/actions` - List actions
  - `POST /api/actions` - Create action
  - `PUT /api/actions/{id}` - Update action
  - `DELETE /api/actions/{id}` - Delete action
  - `GET /api/alerts` - View alert history
  - `GET /api/health` - Health check
- [ ] Add request validation
- [ ] Add authentication (API keys)
- [ ] Add API documentation (OpenAPI/Swagger)

#### Step 10: Webhook Receivers

- [ ] Create webhook endpoints for external integrations:
  - `POST /webhooks/twilio` - Receive Twilio status callbacks
  - `POST /webhooks/custom/{name}` - Generic webhook receiver
- [ ] Add webhook signature verification
- [ ] Implement webhook payload processing
- [ ] Add webhook logging
- [ ] Test with Twilio webhook simulator

#### Step 11: Configuration Management

- [ ] Create configuration file schema (YAML/JSON)
- [ ] Implement configuration loader
- [ ] Add configuration validation
- [ ] Support environment variable overrides
- [ ] Create example configuration files
- [ ] Document all configuration options

### Phase 4: Docker & Deployment (Steps 12-13)

#### Step 12: Dockerization

- [ ] Create `Dockerfile` for application
- [ ] Create `docker-compose.yml`:
  - API service
  - Celery worker
  - Celery beat (scheduler)
  - Redis
  - PostgreSQL
- [ ] Add health checks to all services
- [ ] Create entrypoint scripts
- [ ] Add volume mounts for persistence
- [ ] Test full stack locally

#### Step 13: Production Readiness

- [ ] Add comprehensive logging (structured logging)
- [ ] Implement metrics collection (Prometheus-compatible)
- [ ] Add application monitoring
- [ ] Create backup scripts for database
- [ ] Add security hardening:
  - Environment variable validation
  - Input sanitization
  - Rate limiting
  - CORS configuration
- [ ] Create deployment documentation
- [ ] Add monitoring alerts

### Phase 5: Testing & Documentation (Steps 14-15)

#### Step 14: Testing

- [ ] Write unit tests for all components
- [ ] Create integration tests
- [ ] Add end-to-end tests:
  - Fetch logs → Match pattern → Send email
  - Fetch logs → Match pattern → Trigger webhook
- [ ] Test error scenarios and edge cases
- [ ] Performance testing (handle large log volumes)
- [ ] Load testing for API endpoints

#### Step 15: Documentation

- [ ] Complete README.md with:
  - Quick start guide
  - Installation instructions
  - Configuration guide
  - API documentation
  - Troubleshooting
- [ ] Create DEPLOYMENT.md
- [ ] Create CONFIGURATION.md with examples
- [ ] Add inline code documentation
- [ ] Create architecture diagram
- [ ] Write user guide

## Configuration Examples

### Example Monitoring Rule (JSON)

```json
{
  "name": "Failed Call Detection",
  "description": "Alert when calls fail with specific error codes",
  "enabled": true,
  "log_type": "call",
  "pattern_type": "error_code",
  "pattern_value": "30001,30002,30003",
  "actions": [
    {
      "type": "email",
      "config": {
        "recipients": ["ops@example.com"],
        "subject": "Twilio Call Failure Alert",
        "template": "call_failure"
      }
    },
    {
      "type": "webhook",
      "config": {
        "url": "https://hooks.slack.com/services/...",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        }
      }
    }
  ]
}
```

### Example Threshold Rule

```json
{
  "name": "High Error Rate Detection",
  "description": "Alert when 10+ errors occur within 5 minutes",
  "enabled": true,
  "log_type": "error",
  "pattern_type": "threshold",
  "threshold_count": 10,
  "threshold_window_minutes": 5,
  "actions": [
    {
      "type": "email",
      "config": {
        "recipients": ["oncall@example.com"],
        "subject": "High Twilio Error Rate Alert",
        "priority": "high"
      }
    }
  ]
}
```

## Environment Variables

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/twilio_monitor

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
SMTP_FROM=noreply@example.com

# Application
LOG_LEVEL=INFO
POLL_INTERVAL_SECONDS=300
API_PORT=8000
API_KEY=your_secure_api_key

# Webhook Configuration
WEBHOOK_TIMEOUT_SECONDS=30
WEBHOOK_RETRY_ATTEMPTS=3
```

## Directory Structure

```
twilio-log-monitor/
├── README.md
├── PROJECT_PLAN.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── log.py
│   │   ├── rule.py
│   │   ├── action.py
│   │   └── alert.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── twilio_client.py
│   │   ├── log_fetcher.py
│   │   ├── pattern_matcher.py
│   │   └── action_handler.py
│   ├── actions/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── email.py
│   │   └── webhook.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── logs.py
│   │   │   ├── rules.py
│   │   │   ├── actions.py
│   │   │   └── webhooks.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── log.py
│   │       ├── rule.py
│   │       └── action.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── monitor.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_twilio_client.py
│   ├── test_pattern_matcher.py
│   ├── test_actions.py
│   └── test_api.py
├── templates/
│   ├── email/
│   │   ├── error_notification.html
│   │   └── summary_report.html
└── scripts/
    ├── seed_data.py
    └── run_tests.sh
```

## Success Criteria

- ✅ Successfully polls Twilio API every 5 minutes (configurable)
- ✅ Detects and stores all new logs without duplicates
- ✅ Matches configured patterns with 100% accuracy
- ✅ Sends email notifications within 1 minute of pattern match
- ✅ Triggers webhooks successfully with retry logic
- ✅ API endpoints respond within 200ms for normal queries
- ✅ Handles 1000+ logs per poll cycle without performance degradation
- ✅ Zero data loss during failures (logs stored before processing)
- ✅ Complete test coverage (>80%)
- ✅ Full documentation for deployment and usage

## Future Enhancements (Post-MVP)

1. **Web Dashboard**: React/Vue.js frontend for visual monitoring
2. **SMS Notifications**: Add SMS action handler using Twilio
3. **Slack Integration**: Native Slack app for notifications
4. **Machine Learning**: Anomaly detection for unusual patterns
5. **Multi-Account Support**: Monitor multiple Twilio accounts
6. **Custom Plugins**: Plugin system for custom action handlers
7. **Real-time Websockets**: Live log streaming in dashboard
8. **Historical Analytics**: Trend analysis and reporting
9. **Alert Grouping**: Prevent alert fatigue with intelligent grouping
10. **Incident Management**: Create and track incidents from alerts

## Timeline Estimate

- **Phase 1 (Core Infrastructure)**: 1-2 weeks
- **Phase 2 (Action System)**: 1 week
- **Phase 3 (API & Configuration)**: 1 week
- **Phase 4 (Docker & Deployment)**: 3-4 days
- **Phase 5 (Testing & Documentation)**: 1 week

**Total MVP Timeline**: 4-5 weeks

## Notes

- Start with Phase 1 to establish solid foundation
- Each step should be completed and tested before moving to next
- Maintain incremental git commits for each completed step
- Use feature branches for major components
- Keep configuration flexible for easy customization
- Prioritize error handling and logging from the start
- Document as you build to avoid backlog of documentation work
