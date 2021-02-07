import asyncio
import logging
import os
import pickle
from typing import Callable

import aio_pika
import coloredlogs
from sanic import response
from sanic import Sanic

from .constants import QUEUE_NAME

logger = logging.getLogger(__name__)


def create_fake_data(ndots: int):
    meta = {
        "external_ids": [i for i in range(ndots)],
        "filenames": [f"doc_{i}.txt" for i in range(ndots)],
        "event": "CREATE",
    }
    data = ["A".encode("utf8") * (i + 1) for i in range(ndots)]
    return (meta, data)


def create_sanic_server(send_message: Callable):
    log_config = {"version": 1, "disable_existing_loggers": False, "handlers": {}}

    app = Sanic(__name__, log_config=log_config)

    @app.route("/send", methods=["POST"])
    async def handle(request):
        try:
            subscription_params = dict(request.query_args)
            ndots = subscription_params.get("dots").count(".")
            message = create_fake_data(ndots)

            this_loop = asyncio.get_event_loop()

            # Without await
            this_loop.create_task(send_message(pickle.dumps(message), this_loop))
            # with await
            # await send_message(pickle.dumps(message), this_loop)

            return response.json({"sent": message}, status=200)
        except Exception as e:
            msg = f"Error renewing subscriptions: {e}"
            logger.error(msg)
            return response.json({"error": msg}, status=500)

    return app


async def send_message(message, loop):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/", loop=loop
    )

    channel = await connection.channel()  # type: aio_pika.Channel

    await channel.default_exchange.publish(
        aio_pika.Message(body=message), routing_key=QUEUE_NAME
    )
    await connection.close()


if __name__ == "__main__":

    log_level = logging.DEBUG
    coloredlogs.install(logger=logger, level=log_level)

    logger.info("Starting sanic server")
    app = create_sanic_server(send_message)
    app.run(
        host="0.0.0.0",
        port=7777,
        workers=int(os.getenv("SANIC_WORKERS", 5)),
        backlog=int(os.environ.get("ENV_SANIC_BACKLOG", "100")),
    )
