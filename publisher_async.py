import coloredlogs
import logging
import pika


from constants import QUEUE_NAME
from constants import WATCH_INTERVAL_SECONDS



logger = logging.getLogger(__name__)


class Publisher:
    def __init__(
        self,
        queue_name: str,
        ampq_uri: str = "localhost",
        heartbeat: int = 60,
    ):
        # RabbitMQ parameters
        self._uri = ampq_uri
        self._queue_name = queue_name
        self._heartbeat = heartbeat
        self._stopping = False

        # Connection objects
        self._connection = None
        self._channel = None

    def connect(self):
        logger.info(f"Chasing the 🐇: {self._uri} | {self._queue_name}")

        params = pika.ConnectionParameters(self._uri, heartbeat=self._heartbeat)

        # TODO: Add on_connection_close_callback
        self._connection = pika.SelectConnection(
            parameters=params,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )

    def on_connection_open(self, _unused_connection):
        logger.info(f"Connection opened")
        # Step #3: Open a new channel on the connection
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_connection_open_error(self, _unused_connection, err):
        """Called if the connection to RabbitMQ can't be established."""
        logger.error(f"Connection open failed: {err}")
        # self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        """Invoked by pika when the connection to RabbitMQ is closed unexpectedly"""
        self._channel=None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: {reason}')
            # self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def on_channel_open(self, channel):
        logger.info("Channel opened")
        # Step #4: Bind the channel to the **persistent** queue
        self._channel = channel

        logger.info(f"Declaring queue '{self._queue_name}'")
        self._channel.queue_declare(queue=self._queue_name, durable=True)

        # TODO: Add on_channel_close_callback!?
        # self._channel.add_on_close_callback(self.on_channel_closed)

        # TODO: Add delivery confirmation?
        # self._channel.confirm_delivery(self.on_delivery_confirmation)

    # TODO: Add on_channel_closed

    def send_message(self, message) -> None:
        if self._channel is None or not self._channel.is_open:
            return

        self._channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),  # make message persistent
        )
        logger.info(" [x] Sent %r" % message)

        # Do we need to close the connection!?
        # self.connection.close()

    def stop(self):
        """Close the RabbitMQ channel and connection"""
        logger.info("Stopping")
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        """Close the channel with RabbitMQ"""
        if self._channel is not None:
            logger.info("Closing the channel")
            self._channel.close()

    def close_connection(self):
        """Close the connection to RabbitMQ."""
        if self._connection is not None:
            logger.info("Closing connection")
            self._connection.close()

    def run(self):
        """Run the example code by connecting and then starting the IOLoop."""
        while not self._stopping:
            self._connection = None

            try:
                # Step #1: Connect to RabbitMQ
                self.connect()
                # Step #2: Block on the IOLoop
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if self._connection is not None and not self._connection.is_closed:
                    # Finish closing
                    self._connection.ioloop.start()

        logger.info("Stopped")


if __name__ == "__main__":

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    pub = Publisher(QUEUE_NAME, heartbeat=10)
    pub.run()
