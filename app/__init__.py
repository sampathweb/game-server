from tornado.web import Application
from handler import TicTacToeWSHandler, AcitivityHandler

application = Application([
    # (r'/tic-tac-toe/([a-zA-Z0-9-_]+)$', TicTacToeWSHandler),
    (r'/tic-tac-toe/', TicTacToeWSHandler),
    (r'/activity', AcitivityHandler)
])
