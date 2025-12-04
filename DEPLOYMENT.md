# GiftPulse Deployment Guide

## ✅ Deployment Status: LIVE

**Production URL:** http://104.131.116.144:8000

---

## 🚀 Quick Access

- **API Health:** http://104.131.116.144:8000/api/health
- **OpenAPI Docs:** http://104.131.116.144:8000/docs
- **Monitoring Rules:** http://104.131.116.144:8000/api/rules
- **Actions:** http://104.131.116.144:8000/api/actions
- **Alert History:** http://104.131.116.144:8000/api/alerts

---

## 📊 Current Configuration

### Server Details

- **Provider:** DigitalOcean Droplet
- **IP Address:** 104.131.116.144
- **OS:** Ubuntu 24.04 LTS
- **Specs:** 1GB RAM, 1 CPU, 25GB SSD
- **Cost:** $6/month

### Services Running

```
✅ postgres       - PostgreSQL 15 (port 5432)
✅ redis          - Redis 7 (port 6379)
✅ api            - FastAPI (port 8000)
✅ celery_worker  - Background task processor
✅ celery_beat    - Task scheduler (polls every 5 minutes)
```

### Environment Variables

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
TWILIO_AUTH_TOKEN=<your-twilio-auth-token>

# Email Configuration (Mailtrap or other SMTP)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=<your-smtp-username>
SMTP_PASSWORD=<your-smtp-password>
EMAIL_FROM=giftpulse@monitor.com

# Google Chat Webhook (optional)
GOOGLE_CHAT_WEBHOOK=<your-google-chat-webhook-url>
```

---

## 📋 Pre-configured Monitoring Rules

### 1. Failed Call Detection

- **Type:** Error Code Pattern
- **Monitors:** Twilio calls with error codes 30001-30005
- **Action:** Email to ops@example.com

### 2. SMS Delivery Failure

- **Type:** Status Pattern
- **Monitors:** SMS messages with status: failed, undelivered
- **Action:** Webhook alert

### 3. High Error Rate

- **Type:** Threshold Pattern
- **Monitors:** 10+ errors within 5 minutes
- **Action:** Email alert to oncall@example.com

---

## 🔧 Management Commands

### SSH Access

```bash
ssh root@104.131.116.144
cd giftpulse
```

### Check Service Status

```bash
docker compose ps
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f celery_worker
docker compose logs -f celery_beat
```

### Restart Services

```bash
# All services
docker compose restart

# Specific service
docker compose restart api
```

### Update Application

```bash
git pull
docker compose down
docker compose up -d
```

### Database Access

```bash
# Enter PostgreSQL
docker compose exec postgres psql -U giftpulse -d giftpulse_monitor

# View tables
\dt

# Query logs
SELECT * FROM twilio_logs ORDER BY created_at DESC LIMIT 10;
```

---

## 🔍 Verification Checklist

- [x] API responding to health checks
- [x] Database migrations applied
- [x] Database seeded with example rules
- [x] All 5 Docker services running
- [x] Celery Beat scheduler active (300s interval)
- [x] Celery worker processing tasks
- [x] Monitoring rules accessible via API
- [x] Actions configured and stored

---

## 📈 Monitoring

### Task Schedule

Celery Beat polls Twilio every **5 minutes (300 seconds)** for:

- New call logs
- New message logs
- Monitor alerts from Twilio

### Processing Flow

1. **Celery Beat** triggers `poll_twilio_logs` every 5 minutes
2. **Log Fetcher** retrieves logs from Twilio API
3. **Pattern Matcher** checks logs against active rules
4. **Action Handler** sends alerts (email/webhook/Google Chat)
5. **Alert History** stores all triggered alerts

---

## 🔐 Next Steps (Optional)

### 1. Setup Firewall

```bash
ufw allow 22    # SSH
ufw allow 8000  # API
ufw enable
```

### 2. Configure Domain (Optional)

Point your domain to `104.131.116.144` via A record:

```
giftpulse.yourdomain.com -> 104.131.116.144
```

### 3. Setup HTTPS with Let's Encrypt (Optional)

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d giftpulse.yourdomain.com
```

### 4. Setup Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name 104.131.116.144;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🐛 Troubleshooting

### Service Not Starting

```bash
# Check logs for errors
docker compose logs [service_name]

# Rebuild images
docker compose build --no-cache
docker compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL is healthy
docker compose exec postgres pg_isready -U giftpulse

# Reset database (CAUTION: destroys data)
docker compose down -v
docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_data.py
```

### Celery Not Processing Tasks

```bash
# Check Celery worker logs
docker compose logs celery_worker

# Check Celery beat logs
docker compose logs celery_beat

# Restart Celery services
docker compose restart celery_worker celery_beat
```

---

## 📞 Support

- **GitHub:** https://github.com/ryanlong1004/giftpulse
- **API Documentation:** http://104.131.116.144:8000/docs
- **Health Check:** http://104.131.116.144:8000/api/health
