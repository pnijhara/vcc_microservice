from fastapi import FastAPI
from celery import Celery

app = FastAPI()

celery_app = Celery("tasks", backend="rpc://", broker="pyamqp://myuser:mypassword@<VM1_IP_HERE>//")

@app.get("/")
def read_root():
    return {"message": "FastAPI with RabbitMQ and Celery"}

@app.get("/add/{x}/{y}")
def add_numbers(x: int, y: int):
    task = celery_app.send_task("tasks.add", args=[x, y])
    return {"task_id": task.id, "status": "Processing"}

@app.get("/status/{task_id}")
def get_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result}
