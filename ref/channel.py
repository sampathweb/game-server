# from client_manager import ClientManager
from redis_store import redis_db
import tornadoredis

redis_pub = tornadoredis.Client()
redis_pub.connect()


class GameChannel(object):

    @classmethod
    def gen_key(cls):
        counter = redis_db.incr('channel:count', 1)
        counter = int(counter) + 1
        channel_key = 'channel:' + str(counter)
        return channel_key

    @classmethod
    def new_channel(cls, *args):
        # TODO: Verify that player is not already in the list
        # If exists, reject the call
        channel_key = cls.gen_key()
        for arg in args:
            # subscribe to the channel
            cls.subscribe(channel_key, arg)
        return channel_key

    @classmethod
    def send_message(cls, channel_key, data, sender=None):
        redis_db.publish(channel_key, data)
        # for subscriber in redis_db.smembers(channel_key):
        #     if sender is None or subscriber != sender:
        #         ClientManager.send_message(subscriber, data)

    @classmethod
    def subscribe(cls, channel_key, subscriber_key):
        redis_db.sadd(channel_key, subscriber_key)

    @classmethod
    def unsubscribe(cls, channel_key, subscriber_key):
        redis_db.srem(channel_key, subscriber_key)

    @classmethod
    def close_channel(cls, channel_key):
        redis_db.delete(channel_key)
