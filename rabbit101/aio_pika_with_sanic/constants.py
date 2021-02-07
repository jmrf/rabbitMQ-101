import os

HEARTBEAT = 5
QUEUE_NAME = os.getenv("QUEUE_NAME", "aio-pika-example-q")
