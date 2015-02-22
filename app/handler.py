import json
from tornado.escape import json_decode
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
from datastore import GameStore, ClientManager


class TicTacToeWSHandler(WebSocketHandler):

    def __init__(self, *args, **kwargs):
        self.player_handle = None
        self.client_db = ClientManager()
        self.game_db = GameStore()
        super(TicTacToeWSHandler, self).__init__(*args, **kwargs)

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
        # self.player_handle = player_handle
        self.player_handle = self.game_db.new_player()
        self.client_db.add(self.player_handle, self)
        self._send_message('connect',
            handle=self.player_handle,
            text='Connected to Game Server!')

    def close(self, player_handle):
        self._send_message('dis-connect', text='Dis-connected from Game Server!')
        super(TicTacToeWSHandler, self).close()

    def on_message(self, message):
        data = json_decode(message)
        print data
        data = json.loads(message)
        if data['action'] == 'connect':
            pass
        elif data['action'] == 'ready':
            self.game_db.player_ready(self.player_handle)
        elif data['action'] == 'started':
            pass
        elif data['action'] == 'player-move':
            # Record the player's move and send it to other player
            self.game_db.player_move(self.player_handle, data['move'])
            player2 = self.game_db.get_paired(self.player_handle)
            if player2:
                # Get the handler from ClientManager and send message
                player2_handler = self.client_db[player2]
                if player2_handler:
                    player2_handler.send_message(data)

    def on_close(self):
        # Disconnected from server
        # Send message to Paired user that opponent disconnected
        self.game_db.remove(self.player_handle)
        self.client_db.remove(self.player_handle)


class AcitivityHandler(RequestHandler):
    def get(self):
        # game.game_store.players
        game_db = GameStore()
        return self.write(game_db.players)
