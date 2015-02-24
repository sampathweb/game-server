import redis
import tornadoredis
from opt import REDIS_SERVER_HOST, REDIS_SERVER_PORT

redis_db = redis.StrictRedis(port=REDIS_SERVER_PORT)
redis_pubsub = tornadoredis.Client(port=REDIS_SERVER_PORT)
