#!/bin/sh
# Start script for Railway deployment

# Use PORT environment variable from Railway, default to 8000
PORT=${PORT:-8000}

# Run uvicorn with the dynamic port
exec uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
