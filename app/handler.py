import json
from tornado.escape import json_decode
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
from tictactoe import TicTacToe
import opt
from db_conn import redis_db


class IndexHandler(RequestHandler):

    def get(self):
        self.render("index.html")


class RedisFlushHandler(RequestHandler):

    def get(self):
        redis_db.flushall()
        self.write('Redis Cache Flushed')


class TicTacToeWSHandler(WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super(TicTacToeWSHandler, self).__init__(*args, **kwargs)
        self.handle = None
        self.game = TicTacToe()

    def check_origin(self, origin):
        return True

    def _send_message(self, action, **data):
        message = {}
        message['action'] = action
        for key, val in data.items():
            message[key] = val
        self.write_message(json.dumps(message))

    def _parse_message(self, message):
        data = json.loads(message)
        if data['action'] == 'connect':
            # New socket connection request
            pass

    def open(self):
        # Generate a Player's Handle
        self.handle = self.game.new_player()
        self.application.add_subscriber(self.handle, self)
        self._send_message('connect',
            handle=self.handle,
            hostname=opt.HOSTNAME,
            text='Connected to Game Server!')
        # Subscribe to channel that's same as Player's handle
        # self.listen()

    def close(self, handle):
        self._send_message('dis-connect', text='Dis-connected from Game Server!')
        super(TicTacToeWSHandler, self).close()

    def on_channel_message(self, ch_msg):
        print ch_msg
        if ch_msg.kind == 'subscribe':
            pass
        elif ch_msg.kind == 'message':
            data = json_decode(ch_msg.body)
            self._send_message(**data)

    def on_message(self, message):
        data = json_decode(message)
        print data
        if data['action'] == 'connect':
            pass
        elif data['action'] == 'ready':
            paired_handle = self.game.player_ready(self.handle)
            if not paired_handle:
                self._send_message('wait-pair',
                    text='Waiting for an Opponsent to Join')
        elif data['action'] == 'player-move':
            # Record the player's move and send it to other player
            self.game.player_move(self.handle, data)

    def on_close(self):
        # Disconnected from server
        # Send message to Paired user that opponent disconnected
        self.game.remove(self.handle)
        self.application.remove_subscriber(self.handle, self)


class AcitivityHandler(RequestHandler):
    def get(self):
        # game.game_store.players
        game = TicTacToe()
        return self.write(game.get_all_players())
