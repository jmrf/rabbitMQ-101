import argparse
import datetime as dt

import sys

import logging
import coloredlogs

from . import init_queue_channel
from . import QUEUE_NAME

logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exchange", "-x", required=True, help="exchange name")
    parser.add_argument(
        "--routing_key", "-r", required=True, help="routing key. e.g.: some.routing.key"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = get_args()

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    # Declare the queue and the exchange
    connection, channel = init_queue_channel("localhost", exchange=args.exchange)

    queue = channel.queue_declare(
        queue=QUEUE_NAME, exclusive=False, passive=True, durable=True
    )
    n_msgs = queue.method.message_count

    logger.debug(f"Messages in queue ({QUEUE_NAME}): {n_msgs}")

    # Compose a message
    message = " ".join(sys.argv[1:]) or "info: Hello World!"
    message += " " + dt.datetime.now().isoformat()

    channel.basic_publish(
        exchange=args.exchange, routing_key=args.routing_key, body=message
    )

    print(" [x] Sent %r" % message)
    connection.close()
