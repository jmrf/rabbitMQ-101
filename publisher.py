import coloredlogs
import logging
import pika
import random
import time

from constants import QUEUE_NAME
from constants import HEARTBEAT


logger = logging.getLogger(__name__)


class Watcher:
    def __init__(self, queue_name: str):

        self.queue_name = queue_name
        self.init_queue()
        self.last_send = 0

    def init_queue(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                "localhost", blocked_connection_timeout=5, heartbeat=HEARTBEAT
            )
        )

        # Create the channel **persistent** queue
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def close_queue(self):
        self.connection.close()

    def send_message(self, message):
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),  # make message persistent
        )
        logger.info(" [x] Sent %r" % message)

    def run(self):
        while True:
            logger.info(f"Waiting for tasks....")

            now = time.time()
            if now - self.last_send > HEARTBEAT * 4:
                dots = "." * random.randint(3, 8)

                # send tuple data
                self.send_message(dots)

                self.last_send = time.time()

            time.sleep(0.2)


if __name__ == "__main__":

    # message = " ".join(sys.argv[1:]) or "Hello World!"

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    w = Watcher(QUEUE_NAME)
    w.run()
