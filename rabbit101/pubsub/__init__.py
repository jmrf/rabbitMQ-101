import pika

QUEUE_NAME = "queue_exchange_test"


def init_queue_channel(
    host: str = "localhost", exchange: str = "logs", exchange_type: str = "topic"
):
    # Declare the queue and the exchange
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))

    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)

    return connection, channel
