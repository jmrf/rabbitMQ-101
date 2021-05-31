# rabbitMQ-101

This is a repo with a collection of scripts to understand RabbitMQ.


<!--ts-->
   * [rabbitMQ-101](#rabbitmq-101)
      * [Run](#run)
         * [Basic Dots example](#basic-dots-example)
         * [AIO Pika with Sanic](#aio-pika-with-sanic)
         * [PubSub (ampq exchanges)](#pubsub-ampq-exchanges)

<!-- Added by: jose, at: Mon May 31 19:51:05 UTC 2021 -->

<!--te-->


## Run

You'll need 3 different terminals in the same machine (rabbit listening on localhost):

Run rabbitMQ:

```
./run_rabbit.sh
```

This will launch a dockerized rabbitMQ with the `management` plugin enabled.
Head to `localhost:8080` to access the admin console.

> **note**: Use `guest` both as username and password

### Basic Dots example

A `publisher` reads from terminal a number of dots and send these to the `worker`.
The `worker` then sleeps for as many seconds as dots received.

1. Run the consumer:
```
python -m rabbit101.basic_dots.worker
```

2. Run the publisher:
```
python -m rabbit101.basic_dots.publisher_async
```

### AIO Pika with Sanic

A `publisher` spawns a sanic server and reads from a PSOT request a number of dots
and send these to the `worker`.
The `worker` then writes as many files as dots received.

1. Run the consumer:
```
python -m rabbit101.aio_pika_with_sanic.rx
```

2. Run the publisher:
```
python -m rabbit101.aio_pika_with_sanic.tx
```

3. Send a request:
```bash
curl -X POST 'localhost:7777/send?dots=..' | jq
```

### PubSub (ampq exchanges)

```bash
# run a consumer with a non-anonymous queue
python -m rabbit101.pubsub.rx -x rabbit.test -R test.test

# run a consumer with a anonymous queue
python -m rabbit101.pubsub.rx -a -x rabbit.test -R test.test

# send a message to the exchange (all consumers and monitor the non-anon queue)
python -m rabbit101.pubsub.tx -x rabbit.test -r test.test

```
