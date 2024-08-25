import os

from jaeger import init_jaeger


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    if init_jaeger():
        server.log.info("Jaeger initialized (pid: %s)", worker.pid)
    else:
        server.log.info("Jaeger NOT initialized (pid: %s)", worker.pid)
