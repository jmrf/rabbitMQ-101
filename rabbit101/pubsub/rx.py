import argparse
import time

import logging
import coloredlogs

from . import init_queue_channel
from . import QUEUE_NAME

logger = logging.getLogger(__name__)

global queue_name


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exchange", "-x", required=True, help="exchange name")
    parser.add_argument(
        "--routing_keys",
        "-R",
        required=True,
        help="comma delimited list of routing keys",
    )

    return parser.parse_args()


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

    args = get_args()

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    # Declare the queue and the exchange
    connection, channel = init_queue_channel("localhost", exchange=args.exchange)

    # Create a random Queue
    result = channel.queue_declare(queue=QUEUE_NAME, exclusive=False, durable=True)
    queue_name = result.method.queue

    for k in args.routing_keys.split(","):
        logger.debug(f"Binding queue {queue_name} to key: '{k}'")
        channel.queue_bind(exchange=args.exchange, queue=queue_name, routing_key=k)

    print(" [*] Waiting for logs. To exit press CTRL+C")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()
