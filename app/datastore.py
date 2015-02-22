from collections import defaultdict

class ConnectManager(object):

    def __init__(self):
        # Connection needs to subscribe to Player's Redis KEY
        self.connections = defaultdict(set)

    def add(self, connect_key, handler):
        self.connections[connect_key].add(handler)

    def remove(self, connect_key, handler):
        self.connections[connect_key].remove(handler)

    def send_data(self, connect_key, send_handler, data, send_echo=True):
        handlers = self.connections[connect_key]
        for handler in handlers:
            if send_echo or handler != send_handler:
                handler.send_message(data)


class GameManager(object):

    def __init__(self):
        # This dict needs to be in Redis
        self.players = defaultdict(dict)

    def add(self, player_key):
        # TODO: Verify that player is not already in the list
        # If exists, reject the call
        if player_key in self.players:
            return False
        self.players[player_key]['status'] = 'new'
        self.players[player_key]['pair'] = ''       
        return True

    def player_ready(self, player_key):
        # Find another player that's ready to play
        paired_key = None
        if self.players[player_key]['status'] != 'new':
            return paired_key
        self.players[player_key]['status'] = 'ready'
        self.players[player_key]['pair'] = None

        for player2_key in self.players:
            if player2_key != player_key and \
            self.players[player2_key]['status'] == 'ready':
                # Pair the Players and send them messages
                self.players[player_key]['status'] = 'paired'
                self.players[player_key]['pair'] = player2_key

                self.players[player2_key]['status'] = 'paired'
                self.players[player2_key]['pair'] = player_key
                # Send message to both players
                paired_key = player2_key
                break
        return paired_key

    def set_player_data(self, id, **data):
        for key, val in data.items()
            self.players[id][key] = val
        return True

    def game_over(self, player_key):
        # Remove the player
        paired_key = self.players[player_key]['pair']
        self.players[player_key]['status'] = 'new'
        self.players[player_key]['pair'] = None
        if paired_key:
            self.players[player_key]['status'] = 'new'
            self.players[player_key]['pair'] = None

    def remove(self, player_key):
        # Remove the player
        # TODO Validations
        del self.players[player_key]
