import os

HEARTBEAT = 60
QUEUE_NAME = os.getenv("QUEUE_NAME", "search-watch-queue")
