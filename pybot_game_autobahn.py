###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
import json
import random
import sys
from multiprocessing import Process
# from autobahn.asyncio.websocket import WebSocketClientProtocol, \
#     WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

# import trollius


class MyClientProtocol(WebSocketClientProtocol):

    def __init__(self, *args, **kwargs):
        self.handle = ''
        self.pair_handle = ''
        self.open_positions = ''
        self.my_move = False
        super(MyClientProtocol, self).__init__(*args, **kwargs)

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    # @trollius.coroutine
    def onOpen(self):
        print("WebSocket connection open.")
        # start sending messages every second ..

    def onMessage(self, payload, isBinary):
        data = json.loads(payload)
        print data
        if data['action'] == 'connect':
            self.handle = data['handle']
            data = {}
            data['action'] = 'ready'
            data['handle'] = self.handle
            self.sendMessage(json.dumps(data))
            # yield trollius.sleep(1)
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
            print 'My Handle: ', self.handle, 'Pair Handle: ', self.pair_handle, 'Result: ', data['result'], ' : ', data['win_handle']
            # Game Over
            self.my_move = False
            data = {}
            data['action'] = 'ready'
            data['handle'] = self.handle
            self.sendMessage(json.dumps(data))
            # yield trollius.sleep(1)
        if self.my_move:
            # select a piece to move
            self.my_move = False
            data = {}
            data['action'] = 'player-move'
            data['handle'] = self.handle
            data['move'] = random.choice(self.open_positions.split(';'))
            self.sendMessage(json.dumps(data))
            # yield trollius.sleep(1)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


def main_async(worker_numb):
    print sys.argv
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        ws_host = '127.0.0.1'
        ws_port = 8001
    else:
        ws_host = "websocket-ha-test.ovlizj.0001.usw1.cache.amazonaws.com"
        ws_port = 80
    # + ':' + str(ws_port) +
    ws_host_url = 'ws://' + ws_host + ':' + str(ws_port) + '/tic-tac-toe/'
    factory = WebSocketClientFactory(ws_host_url, debug=False)
    factory.protocol = MyClientProtocol

    loop = trollius.get_event_loop()
    coro = loop.create_connection(factory, ws_host, ws_port)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()


def main(worker_numb):
    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    print sys.argv
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        ws_host = '127.0.0.1'
        ws_port = 8001
    else:
        ws_host = "websocket-ha-test.ovlizj.0001.usw1.cache.amazonaws.com"
        ws_port = 80
    # + ':' + str(ws_port) +
    ws_host_url = 'ws://' + ws_host + ':' + str(ws_port) + '/tic-tac-toe/'
    factory = WebSocketClientFactory(ws_host_url, debug=False)
    factory.protocol = MyClientProtocol
    reactor.connectTCP(ws_host, ws_port, factory)
    reactor.run()


if __name__ == '__main__':
    # Setup a list of processes that we want to run
    processes = [Process(target=main, args=(x,)) for x in range(4)]

    # Run processes
    for p in processes:
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()
