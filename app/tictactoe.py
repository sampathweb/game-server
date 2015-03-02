import json
from db_conn import redis_db


class TicTacToe(object):

    def __init__(self):
        self.winning_combos = []
        # Define the winning combinations by row
        for row in range(3):
            win_set = set()
            for col in range(3):
                win_set.add(str(row) + "," + str(col))
            self.winning_combos.append(win_set)
        # Define the winning combinations by Col
        for col in range(3):
            win_set = set()
            for row in range(3):
                win_set.add(str(row) + "," + str(col))
            self.winning_combos.append(win_set)
        # Define the winning combinations by Diagonal
        self.winning_combos.append(set(["0,0", "1,1", "2,2"]))
        self.winning_combos.append(set(["0,2", "1,1", "2,0"]))

    def gen_key(self):
        counter = redis_db.incr("handle:count", 1)
        counter = int(counter) + 1
        player_key = "player:" + str(counter)
        return player_key

    def init_player_data(self, handle, status="new", pair=""):
        player_data = {}
        player_data["handle"] = handle
        player_data["status"] = status
        player_data["pair"] = pair
        player_data["my_moves"] = ""
        return player_data

    def new_player(self):
        player_key = self.gen_key()
        player_data = self.init_player_data(player_key, "new")
        redis_db.hmset(player_key, player_data)
        return player_key

    def player_ready(self, player_key):
        # Find another player that"s ready to play
        paired_key = None
        player_data = self.init_player_data(player_key, status="ready")
        redis_db.hmset(player_key, player_data)

        for player2_key in redis_db.keys("player:*"):
            if player2_key != player_key \
                    and redis_db.hget(player2_key, "status") == "ready":
                # Pair the Players and send them messages
                player_data = self.init_player_data(player_key, "paired", player2_key)
                redis_db.hmset(player_key, player_data)

                player2_data = self.init_player_data(player2_key, "paired", player_key)
                redis_db.hmset(player2_key, player2_data)

                # Send Paired to both players
                print 'pair player: ', player_key, ' and ', player2_key
                data = {}
                data["action"] = "paired"
                data["pair"] = player2_key
                redis_db.publish(player_key, json.dumps(data))
                data = {}
                data["action"] = "paired"
                data["pair"] = player_key
                redis_db.publish(player2_key, json.dumps(data))
                print 'Start Game : ', player_key, ' and ', player2_key

                # Send message to both players
                data = {}
                data["action"] = "game-start"
                data["next_handle"] = player_key
                data["valid-moves"] = self.open_positions()
                # Send message to channel of both players
                for channel_key, paired_key in [(player_key, player2_key),
                        (player2_key, player_key)]:
                    redis_db.publish(channel_key, json.dumps(data))
                print 'Start Game Done : ', player_key, ' and ', player2_key
                break
        return player2_key

    def open_positions(self, moves_player_a="", moves_player_b=""):
        """Returns List of Open positions"""
        open_loc = set()
        for row in range(3):
            for col in range(3):
                open_loc.add(str(row) + ',' + str(col))
        moves_player_a = moves_player_a.split(";")
        moves_player_b = moves_player_b.split(";")
        open_loc = open_loc - set(moves_player_a)
        open_loc = open_loc - set(moves_player_b)
        return ';'.join(list(open_loc))

    def check_result(self, moves_player_a, moves_player_b):
        """Returns True if Game has ended with a Winner or Draw, else returns False"""
        result = None
        moves_player_a = moves_player_a.split(";")
        moves_player_b = moves_player_b.split(";")
        for win_set in self.winning_combos:
            if win_set.issubset(moves_player_a):
                result = "won"
                break
            elif win_set.issubset(moves_player_b):
                result = "lost"
                break
        if not result:
            rem_positions = 9 - len(moves_player_a) - len(moves_player_b)
            if rem_positions == 0:
                result = "draw"
        return result

    def player_move(self, player_key, data):
        player_data = redis_db.hgetall(player_key)
        if player_data["my_moves"]:
            player_data["my_moves"] += ";" + data["move"]
        else:
            player_data["my_moves"] = data["move"]
        redis_db.hset(player_key, "my_moves", player_data["my_moves"])
        player2_key = player_data["pair"]
        player2_data = redis_db.hgetall(player2_key)
        # Put the message on the channel of Player2
        redis_db.publish(player2_key, json.dumps(data))
        # Check the game result
        moves_player_1 = player_data["my_moves"]
        moves_player_2 = player2_data["my_moves"]
        result = self.check_result(moves_player_1, moves_player_2)
        if result:
            player_data["status"] = "game-end"
            player2_data["status"] = "game-end"
            redis_db.hmset(player_key, player_data)
            redis_db.hmset(player2_key, player2_data)
            # Send the result on the channel
            data = {}
            data["action"] = "game-end"
            data["next_handle"] = ""
            data["result"] = result
            if result == "draw":
                data["win_handle"] = ""
            elif result == "won":
                data["win_handle"] = player_key
            elif result == "lost":
                data["win_handle"] = player2_key
        else:
            data = {}
            data["action"] = "valid-moves"
            data["next_handle"] = player_data["pair"]
            data["valid-moves"] = self.open_positions(moves_player_1, moves_player_2)
        for channel_key in [player_key, player2_key]:
            redis_db.publish(channel_key, json.dumps(data))

    def get_paired(self, player_key):
        return redis_db.hget(player_key, "pair")

    def set_player_data(self, player_key, **data):
        redis_db.hmset(player_key, data)
        return True

    def get_all_players(self):
        player_keys = redis_db.keys("player:*")
        players = {}
        for player_key in player_keys:
            players[player_key] = redis_db.hgetall(player_key)
        return players

    def game_over(self, player_key):
        # Remove the player
        player2_key = redis_db.hget(player_key, "pair")
        player_data = self.init_player_data(player_key, "new")
        redis_db.hmset(player_key, player_data)
        player_data = self.init_player_data(player2_key, "new")
        redis_db.hmset(player2_key, player_data)

    def remove(self, player_key):
        # Remove the player
        return redis_db.delete(player_key)
