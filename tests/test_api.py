import os
import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import celery_app


@pytest.fixture(autouse=True)
def set_eager_mode(monkeypatch):
    # Run Celery tasks synchronously for tests and use in-memory backend
    celery_app.celery.conf.update(
        task_always_eager=True,
        task_store_eager_result=True,
        broker_url='memory://',
        result_backend='cache+memory://',
    )
    yield


def test_create_and_get_sentiment_task():
    client = TestClient(app)
    payload = {"type": "sentiment", "text": "I love sunny days"}
    r = client.post('/tasks', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert 'task_id' in data
    task_id = data['task_id']

    # Immediately fetch result (since tasks run eagerly)
    r2 = client.get(f'/tasks/{task_id}')
    assert r2.status_code == 200
    j = r2.json()
    assert j['status'] in ('SUCCESS', 'SUCCESS')
    assert isinstance(j['result'], dict)
    assert 'polarity' in j['result']


def test_keywords_task():
    client = TestClient(app)
    payload = {"type": "keywords", "text": "apple banana apple fruit banana orange", "top_k": 2}
    r = client.post('/tasks', json=payload)
    assert r.status_code == 200
    task_id = r.json()['task_id']
    r2 = client.get(f'/tasks/{task_id}')
    assert r2.status_code == 200
    j = r2.json()
    assert 'keywords' in j['result']
