import sys
import pika
import time

import logging
import coloredlogs

from tqdm import tqdm

from . import init_queue_channel
from . import QUEUE_NAME

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    # Declare the queue and the exchange
    connection, channel = init_queue_channel("localhost")

    n_msgs = channel.queue_declare(
            queue=QUEUE_NAME, passive=True
    ).method.message_count

    logger.debug(f"Messages in queue ({QUEUE_NAME}): {n_msgs}")

    # Compose a message
    message = ' '.join(sys.argv[1:]) or "info: Hello World!"

    channel.basic_publish(
        exchange='logs',
        routing_key='',
        body=message + f" {i}"
    )

    print(" [x] Sent %r" % message)
    connection.close()
