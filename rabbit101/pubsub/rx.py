import time
import sys

import logging
import coloredlogs

from . import init_queue_channel
from . import QUEUE_NAME

logger = logging.getLogger(__name__)

global queue_name


def callback(ch, method, properties, body):
    print(" [x] %r" % body)

    n_msgs = channel.queue_declare(
        queue=queue_name, passive=True, durable=True
    ).method.message_count

    logger.debug(f"Messages in queue ({queue_name}): {n_msgs}")

    time.sleep(10)

    # no ACK because the connection will be closed by the Sender after sending
    # ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":

    _use_named_q = bool(int(sys.argv[1]))

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    # Declare the queue and the exchange
    connection, channel = init_queue_channel("localhost")

    _queue_name = QUEUE_NAME if _use_named_q else ""
    _exclusive = False if _use_named_q else True
    result = channel.queue_declare(queue=_queue_name, exclusive=_exclusive, durable=True)

    queue_name = result.method.queue

    logger.debug(f"Binding to queue: '{queue_name}'")
    channel.queue_bind(exchange="logs", queue=queue_name)

    print(" [*] Waiting for logs. To exit press CTRL+C")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()
