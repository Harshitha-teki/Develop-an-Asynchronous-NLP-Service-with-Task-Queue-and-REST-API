# Async NLP Service (FastAPI + Celery)

This repository provides a minimal asynchronous NLP service using FastAPI for the REST API and Celery + Redis for task queuing.

Features
- Submit text-processing tasks (sentiment, keywords, tokenize) via REST API
- Asynchronous task processing by a Celery worker
- Docker Compose for quick startup (includes Redis)

Quickstart (Docker)
1. Build and start services:

   docker-compose up --build

2. Submit a task (example):

   curl -X POST "http://localhost:8000/tasks" -H "Content-Type: application/json" -d "{\"type\": \"sentiment\", \"text\": \"I love this product!\"}"

3. Check result:

   curl http://localhost:8000/tasks/<task_id>

Run locally (without Docker)
- Install requirements: python -m pip install -r requirements.txt
- Start Redis (e.g., via Docker: docker run -p 6379:6379 redis)
- Start API: uvicorn app.main:app --reload
- Start worker: celery -A app.celery_app.celery worker --loglevel=info

Tests
- The repository includes a small pytest test that runs tasks synchronously (Celery eager mode). To run tests:

   pytest -q

Notes
- NLTK data will be downloaded on first run if missing.
- For production, secure Redis and use persistent volumes.
