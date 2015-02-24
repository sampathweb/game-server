import islocal
import socket

IS_LOCAL = islocal.IS_LOCAL

WS_PORT = 8001 if IS_LOCAL else 80

REDIS_SERVER_HOST = 'localhost' if IS_LOCAL else "websocket-ha-test.ovlizj.0001.usw1.cache.amazonaws.com"
REDIS_SERVER_PORT = 6379

HOSTNAME = socket.gethostname()
