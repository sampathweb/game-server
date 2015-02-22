from collections import defaultdict


class ClientManager(object):

    # Connect client player to handler
    connections = dict()

    def add(self, connect_key, handler):
        self.connections[connect_key] = handler

    def remove(self, connect_key):
        del self.connections[connect_key]

    def send_data(self, connect_key, data, send_echo=True):
        handler = self.connections[connect_key]
        handler.send_message(data)


class GameStore(object):

    # This dict needs to be in Redis
    players = defaultdict(dict)
    player_count = 0

    def new_player(self):
        # TODO: Verify that player is not already in the list
        # If exists, reject the call
        GameStore.player_count += 1
        print GameStore.player_count
        player_key = 'player-' + str(GameStore.player_count)
        print player_key
        self.players[player_key]['status'] = 'new'
        self.players[player_key]['pair'] = ''
        return player_key

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
                self.players[player_key]['my_moves'] = []
                self.players[player_key]['opp_moves'] = []

                self.players[player2_key]['status'] = 'paired'
                self.players[player2_key]['pair'] = player_key
                self.players[player2_key]['my_moves'] = []
                self.players[player2_key]['opp_moves'] = []
                # Send message to both players
                paired_key = player2_key
                break
        return paired_key

    def player_move(self, player_key, move):
        self.players[player_key]['my_moves'].append(move)


    def get_paired(self, player_key):
        return self.players[player_key]['pair']

    def set_player_data(self, id, **data):
        for key, val in data.items():
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
