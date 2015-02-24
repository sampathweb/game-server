import json
from tornado.web import Application
import tornado.websocket
from tornadoredis.pubsub import BaseSubscriber

from handler import TicTacToeWSHandler, AcitivityHandler
from db_conn import redis_db, redis_pubsub


class RedisSubscriber(BaseSubscriber):

    def on_message(self, msg):
        """Handles new messages on the Redis Channel."""
        if msg and msg.kind == 'message':
            subscribers = list(self.subscribers[msg.channel])
            for subscriber in subscribers:
                try:
                    subscriber.write_message(msg.body)
                except tornado.websocket.WebSocketClosedError:
                    # Remove dead peer
                    self.unsubscribe(msg.channel, subscriber)
        super(RedisSubscriber, self).on_message(msg)


class GameApplication(Application):

    def __init__(self, **kwargs):
        routes = [
            (r'/tic-tac-toe/', TicTacToeWSHandler),
            (r'/activity/', AcitivityHandler)
        ]
        super(GameApplication, self).__init__(routes, **kwargs)
        self.subscriber = RedisSubscriber(redis_pubsub)
        self.publisher = redis_db

    def add_subscriber(self, channel, subscriber):
        self.subscriber.subscribe(['all', channel], subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriber.unsubscribe(channel, subscriber)
        self.subscriber.unsubscribe('all', subscriber)

    def broadcast(self, message, channel=None, sender=None):
        channel = 'all' if channel is None else channel
        message = json.dumps({
            'sender': sender,
            'message': message
        })
        self.publisher.publish(channel, message)
