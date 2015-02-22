import json
from tornado.websocket import WebSocketHandler
from datastore import GameManager, ConnectManager


class TicTacToeWSHandler(WebSocketHandler):

    connections = ConnectManager()
    game_store = GameManager()

    def check_origin(self, origin):
        return True

    def _send_message(self, action, **data):
        message = {}
        message['action'] = action
        for key, val in data.items():
            message[key] = val
        self.write_message(json.dumps(message))

    def _parse_message(self, message):
        data = json.loads(message);
        if data['action'] == 'connect':
            # New socket connection request

    def open(self, player_handle):
        if game_store.add(player_handle):
            connections.add(player_handle, self)
            self._send_message('connect', text='Connected to Game Server!')
        else:
            # Connection already exists, Ask Player to select different handle
            self._send_message('Error', text=player_handle + ' already Taken.  Choose a different username')
            self.close()


    def on_message(self, message):
        print 'message received %s: ' % message

    def on_close(self):
        self._send_message('dis-connect', text='Dis-connected from Game Server!')
