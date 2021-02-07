# rabbitMQ-101

This is a repo with a collection of scripts to understand RabbitMQ.


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
