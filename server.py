import logging
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.options
from tornado.options import define, options

from app import GameApplication
from app.opt import WS_PORT

define("port", default=WS_PORT, help="run on the given port", type=int)
define("debug", default=False, type=bool)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    application = GameApplication(debug=options.debug)
    http_server = HTTPServer(application)
    http_server.listen(port=options.port)
    logging.info('Starting server on localhost:{}'.format(options.port))
    IOLoop.instance().start()
