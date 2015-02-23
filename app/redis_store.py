import redis
from opt import REDIS_SERVER_HOST, REDIS_SERVER_PORT

redis_db = redis.StrictRedis(port=REDIS_SERVER_PORT)
