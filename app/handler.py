import json
from tornado.escape import json_decode
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
import tornado.gen
from tictactoe import TicTacToe
from client_manager import ClientManager
import tornadoredis
from opt import REDIS_SERVER_HOST, REDIS_SERVER_PORT


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
        ClientManager.add(self.handle, self)
        self._send_message('connect',
            handle=self.handle,
            text='Connected to Game Server!')
        # Subscribe to channel that's same as Player's handle
        self.listen()

    @tornado.gen.engine
    def listen(self):
        # Make a Redis connection
        redis_pub = tornadoredis.Client(port=REDIS_SERVER_PORT)
        redis_pub.connect()
        yield tornado.gen.Task(self.redis_pub.subscribe, self.handle)
        self.redis_pub.listen(self.on_channel_message)

    def close(self, handle):
        self._send_message('dis-connect', text='Dis-connected from Game Server!')
        super(TicTacToeWSHandler, self).close()

    def on_channel_message(self, ch_msg):
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
        ClientManager.remove(self.handle)
        if self.redis_pub and self.redis_pub.subscribed:
            self.redis_pub.unsubscribe(self.handle)
            self.redis_pub.disconnect()


class AcitivityHandler(RequestHandler):
    def get(self):
        # game.game_store.players
        game = TicTacToe()
        return self.write(game.get_all_players())
