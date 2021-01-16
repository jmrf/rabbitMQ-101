import logging

import coloredlogs
import pika

from .constants import QUEUE_NAME


logger = logging.getLogger(__name__)


class Watcher:
    def __init__(self, queue_name: str):

        self.queue_name = queue_name
        self.init_queue()
        self.last_send = 0

    def init_queue(self):
        self.connection = pika.BlockingConnection(
            # for connection no to die while blocked waiting for inputs
            # we must set the heartbeat to 0 (although is discouraged)
            pika.ConnectionParameters(
                "localhost", blocked_connection_timeout=5, heartbeat=0
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
            logger.info(f"Waiting for a 📨 to send")

            dots = input(f"Write some dots\t\t")

            # send tuple data
            self.send_message(dots)


if __name__ == "__main__":

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    w = Watcher(QUEUE_NAME)
    w.run()
