import islocal

IS_LOCAL = islocal.IS_LOCAL

WS_PORT = 8001 if IS_LOCAL else 80

REDIS_SERVER_HOST = "http://0.0.0.0"
REDIS_SERVER_PORT = 7777
