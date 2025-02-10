# FastAPI, Celery, and RabbitMQ Microservice Setup

## Overview
This guide covers setting up FastAPI with RabbitMQ on VM1 and Celery with RabbitMQ on VM2, both running on separate Ubuntu Server virtual machines connected via NAT in VirtualBox.

## Step-by-Step Setup

### Step 1: Download and Setup VirtualBox
1. Download and install VirtualBox from [VirtualBox website](https://www.virtualbox.org/).
2. Download Ubuntu Server ISO from [Ubuntu website](https://ubuntu.com/download/server/arm) for each VM.
3. Create VMs in VirtualBox, configuring each with the Ubuntu Server ISO.

### Step 2: Configure Network Settings
1. Set up NAT Network in VirtualBox to allow VMs to communicate.
2. Assign the same NAT network subnet to each VM's network settings.

### Step 3: Install Dependencies

#### VM1 (FastAPI Server)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv rabbitmq-server
mkdir fastapi_server && cd fastapi_server
source venv/bin/activate
pip install fastapi uvicorn
```

#### VM2 (Celery Worker)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv rabbitmq-server
mkdir celery_worker && cd celery_worker
source venv/bin/activate
pip install celery
```

### Step 4: Configure RabbitMQ on VM1 and VM2
1. Enable and start RabbitMQ server on both VMs.
2. Create a RabbitMQ user on VM1:
   ```bash
   sudo rabbitmqctl add_user myuser mypassword
   sudo rabbitmqctl set_user_tags myuser administrator
   sudo rabbitmqctl set_permissions -p / myuser ".*" ".*" ".*"
   ```

### Step 5: Create `tasks.py` on VM2 (Celery Worker)
```python
from celery import Celery

VM1_IP = "<VM1_IP_HERE>"  # Replace with actual VM1 IP

celery_app = Celery("tasks")
celery_app.conf.update(
    broker_url=f"pyamqp://myuser:mypassword@{VM1_IP}//",
    result_backend="rpc://"
)

@celery_app.task
def add(x, y):
    return x + y
```
Start Celery worker:
```bash
celery -A tasks worker --loglevel=info
```

### Step 6: Create `main.py` on VM1 (FastAPI Server)
```python
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
```
Start FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing the Setup
### Send an Addition Task (From VM1)
```bash
curl -X GET http://<VM1_IP>:8000/add/5/10
```
### Check Task Status (From VM1)
```bash
curl -X GET http://<VM1_IP>:8000/status/<TASK_ID>
```
