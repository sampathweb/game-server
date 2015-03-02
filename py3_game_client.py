#!/usr/bin/env python
import json
import asyncio
from time import sleep
import random
from multiprocessing import Process
import websockets


class GameClient:
    def __init__(self):
        self.handle = ''
        self.pair_handle = ''
        self.open_positions = ''
        self.my_move = False

    def handle_message(self, data):
        print('Msg Recvd: ', data)
        send_data = None
        if data['action'] == 'connect':
            self.handle = data['handle']
            send_data = {}
            send_data['action'] = 'ready'
            send_data['handle'] = self.handle
        elif data['action'] == 'paired':
            self.pair_handle = data['pair']
        elif data['action'] == 'game-start':
            if data['next_handle'] == self.handle:
                self.my_move = True
            else:
                self.my_move = False
            self.open_positions = data['valid-moves']
        elif data['action'] == 'valid-moves':
            if data['next_handle'] == self.handle:
                self.open_positions = data['valid-moves']
                self.my_move = True
        elif data['action'] == 'player-move':
            pass
        elif data['action'] == 'game-end':
            print('My Handle: ', self.handle, 'Pair Handle: ', self.pair_handle, 'Result: ', data['result'], ' : ', data['win_handle'])
            # Game Over
            self.my_move = False
            send_data = {}
            send_data['action'] = 'ready'
            send_data['handle'] = self.handle
        if self.my_move:
            # select a piece to move
            self.my_move = False
            send_data = {}
            send_data['action'] = 'player-move'
            send_data['handle'] = self.handle
            send_data['move'] = random.choice(self.open_positions.split(';'))
        return send_data


def open_websocket():
    while True:
        sleep(2)
        try:
            websocket = websockets.connect('ws://localhost:8001/tic-tac-toe/')
            if websocket.open:
                break
        except Exception:
            pass  # Keep trying
    return websocket


@asyncio.coroutine
def main_websocket():
    websocket = yield from websockets.connect('ws://localhost:8001/tic-tac-toe/')
    game_client = GameClient()
    while True:
        message = yield from websocket.recv()
        if message is None:
            # Connection closed, reconnect
            sleep(2)
            websocket = yield from websockets.connect('ws://localhost:8001/tic-tac-toe/')
            game_client = GameClient()
        else:
            data = json.loads(message)
            send_data = game_client.handle_message(data)
            if send_data:
                sleep(1)  # wait for 1 seconds before sending messages
                yield from websocket.send(json.dumps(send_data))


def main(worker_numb):
    asyncio.get_event_loop().run_until_complete(main_websocket())

if __name__ == '__main__':
    # Setup a list of processes that we want to run
    processes = [Process(target=main, args=(x,)) for x in range(100)]

    # Run processes
    for p in processes:
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()
