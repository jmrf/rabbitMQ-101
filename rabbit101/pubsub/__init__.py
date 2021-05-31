import pika

QUEUE_NAME = "exchange_test_queue"


def init_queue_channel(
    host: str = "localhost", exchange: str = "logs", exchange_type: str = "topic"
):
    # Declare the queue and the exchange
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))

    channel = connection.channel()
    channel.exchange_declare(
        exchange=exchange, exchange_type=exchange_type, passive=True, durable=True
    )

    return connection, channel
