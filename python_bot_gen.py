from multiprocessing import Process
from time import sleep
import json
import random
import websocket

THREAD_COUNT = 10
HOST = "localhost:8001"
WS_URL = 'ws://%s/tic-tac-toe/' % HOST


def worker(worker_num=1):
    # while True:
    #     try:
    # Connect to WS Server, Play the game until connection close
    handle = ""
    try:
        ws = websocket.create_connection("ws://127.0.0.1:8001/tic-tac-toe/")
        # Get the Connect Event
        while True:
            message = ws.recv()
            data = json.loads(message)
            if data['action'] == 'connect':
                handle = data['handle']
                break
        # Send the ready to play
        # Continue Playing
        game_cnt = 0
        sleep(2)
        while True:
            game_cnt += 1
            print 'Send the Start Game: '
            if game_cnt > 1:
                break
            data = {}
            data['action'] = 'ready'
            data['handle'] = handle
            ws.send(json.dumps(data))
            print 'Message Sent: ', data
            # Now, wait for game to start
            while True:
                sleep(2)
                print 'Waiting for Server Message.'
                message = ws.recv()
                print message
                data = json.loads(message)
                if data['action'] == 'paired':
                    pair_handle = data['pair']
                    # Wait for game-start message
                elif data['action'] == 'game-start':
                    if data['next_handle'] == handle:
                        my_move = True
                    else:
                        my_move = False
                    open_positions = data['valid-moves']
                    break
            print 'game-started: ', handle, 'vs. ', pair_handle
            # Game Started
            while True:
                if my_move:
                    # select a piece to move
                    data = {}
                    data['action'] = 'player-move'
                    data['move'] = random.choice(open_positions.split(';'))
                    ws.send(json.dumps(data))
                    my_move = False
                else:
                    print 'waiting for message:'
                    message = ws.recv()
                    print message
                    data = json.loads(message)
                    if data['action'] == 'game-end':
                        print 'My Handle: ', handle, 'Pair Handle: ', pair_handle, 'Result: ', data['result'], ' : ', data['win_handle']
                        break
                    elif data['action'] == 'valid-moves':
                        if data['next_handle'] == handle:
                            open_positions = data['valid-moves']
                            my_move = True
    # except Exception as e:
    #     print 'Error on thread', worker_num, e
    finally:
        ws.close()


# def main():
#         t = threading.Thread(target=worker, args=[i])
#         t.start()
#     while True:
#         sleep(3)

if __name__ == '__main__':
    players = []
    for i in range(2):
        p = Process(target=worker)
        p.start()
        players.append(p)
    for p in players:
        p.join()
