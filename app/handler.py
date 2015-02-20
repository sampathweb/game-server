from tornado.websocket import WebSocketHandler


class TicTacToeWSHandler(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print 'new connection'
        self.write_message("Connected!")

    def on_message(self, message):
        print 'message received %s: ' % message

    def on_close(self):
        print 'connection closed'
