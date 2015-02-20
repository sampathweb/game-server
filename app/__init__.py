from tornado.web import Application

from handler import TicTacToeWSHandler


application = Application([
    (r'/tic-tac-toe', TicTacToeWSHandler),
])
