from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from celery.result import AsyncResult
from . import tasks
from .celery_app import celery

app = FastAPI(title="Async NLP Service")


class TaskRequest(BaseModel):
    type: str
    text: str
    top_k: Optional[int] = 5


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tasks")
async def create_task(req: TaskRequest):
    ttype = req.type.lower()
    if ttype == 'sentiment':
        async_result = tasks.sentiment_analysis.delay(req.text)
    elif ttype == 'keywords':
        async_result = tasks.extract_keywords.delay(req.text, req.top_k)
    elif ttype == 'tokenize':
        async_result = tasks.tokenize.delay(req.text)
    else:
        raise HTTPException(status_code=400, detail="Unknown task type")

    return {"task_id": async_result.id, "status": async_result.status}


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    res = AsyncResult(task_id, app=celery)
    if res is None:
        raise HTTPException(status_code=404, detail="Task not found")
    out = {
        "task_id": task_id,
        "status": res.status,
        "result": res.result if res.ready() else None,
    }
    return out
