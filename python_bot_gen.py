import sys
from multiprocessing import Process
from time import sleep
import json
import random
import websocket

THREAD_COUNT = 10
HOST = "localhost:8001"
WS_URL = 'ws://%s/tic-tac-toe/' % HOST


def worker(worker_num, ws_url):
    # while True:
    #     try:
    # Connect to WS Server, Play the game until connection close
    handle = ""
    while True:
        sleep(1)
        try:
            ws = websocket.create_connection(ws_url)
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
            sleep(1)
            while True:
                # Start of New Game
                while True:
                    game_cnt += 1
                    # print 'Send the Start Game: '
                    data = {}
                    data['action'] = 'ready'
                    data['handle'] = handle
                    ws.send(json.dumps(data))
                    # print 'Message Sent: ', data
                    # Now, wait for game to start
                    while True:
                        # sleep(2)
                        # print 'Waiting for Server Message.'
                        message = ws.recv()
                        sleep(1)
                        # print message
                        data = json.loads(message)
                        if data['action'] == 'paired':
                            pair_handle = data['pair']
                            # Wait for game-start message
                        elif data['action'] == 'game-start':
                            print 'Game Start: ', handle, ' vs. ', pair_handle
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
                            # print 'waiting for message:'
                            message = ws.recv()
                            # print message
                            data = json.loads(message)
                            if data['action'] == 'game-end':
                                print 'Game End: ', handle, 'vs. ', pair_handle, 'Result: ', data['result'], ' : ', data['win_handle']
                                break
                            elif data['action'] == 'valid-moves':
                                if data['next_handle'] == handle:
                                    open_positions = data['valid-moves']
                                    my_move = True
        # except Exception as e:
        #     print 'Error on thread', worker_num, e
        except Exception:
            pass
        finally:
            ws.close()


# def main():
#         t = threading.Thread(target=worker, args=[i])
#         t.start()
#     while True:
#         sleep(3)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        numb_workers = int(sys.argv[1])
    else:
        sys.exit(0)

    if len(sys.argv) > 2 and sys.argv[2] == 'local':
        ws_url = 'ws://localhost:8001/tic-tac-toe/'
    else:
        ws_url = "ws://websockets-test-ha-1776378039.us-west-1.elb.amazonaws.com/tic-tac-toe/"

    # Setup a list of processes that we want to run
    processes = [Process(target=worker, args=(x, ws_url)) for x in range(numb_workers)]

    # Run processes
    for p in processes:
        sleep(0.5)
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()

    # players = []
    # for i in range(40):
    #     p = Process(target=worker, )
    #     p.start()
    #     players.append(p)
    # for p in players:
    #     p.join()
