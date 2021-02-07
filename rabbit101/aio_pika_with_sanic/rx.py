import logging
import os
import pickle
import sys

import coloredlogs
import pika

from .constants import HEARTBEAT
from .constants import QUEUE_NAME


logger = logging.getLogger(__name__)


def save_file(event) -> None:
    meta, data = event

    print(f"Received {len(data)} events")

    if meta.get("event") == "CREATE":
        file_names = meta.get("filenames")

        for filename, dat in zip(file_names, data):
            file_path = os.path.join("QueueData", filename)

            # write bytes to disk
            with open(file_path, "wb") as f:
                f.write(dat)


def callback(ch, method, properties, body):
    try:
        events = pickle.loads(body)
        save_file(events)

        logger.info("🍻 Done")
    except Exception as e:
        logger.error(f"Error in callback: {e}")
        logger.exception(e)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", heartbeat=HEARTBEAT)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("⌛ Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
