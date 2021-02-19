import logging
import time

import coloredlogs
import pika

from .constants import QUEUE_NAME


logger = logging.getLogger(__name__)


class Publisher:
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

    def get_q_count(self):
        return self.channel.queue_declare(
            queue=self.queue_name, passive=True
        ).method.message_count

    def close_queue(self):
        self.connection.close()

    def wait_on_q_limit(self, lim=5):
        msg_in_q = self.get_q_count()
        print(f"found {msg_in_q} messages in the queue...")
        while msg_in_q > lim:
            print(f"waiting... ({msg_in_q} remaining)")
            time.sleep(1)
            msg_in_q = self.get_q_count()

    def send_message(self, message):
        self.wait_on_q_limit(lim=2)
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

    w = Publisher(QUEUE_NAME)
    w.run()
