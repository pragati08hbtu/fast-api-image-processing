#!/bin/sh

# Start the FastAPI server in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the Celery worker
celery -A main.celery worker --loglevel=info

# Wait for all background jobs to complete
wait
