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
