from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import application


if __name__ == '__main__':
    http_server = HTTPServer(application)
    http_server.listen(8888)
    IOLoop.instance().start()
