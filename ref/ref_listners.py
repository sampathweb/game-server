'{u"action": u"player-move", u"handle": u"player:16", "next_handle": "player:17"}'


ssh fivestars@ws.nerfstars.com
LISTENERS = []
 
 
def redis_listener():
    r = redis.Redis()
    ps = r.pubsub()
    ps.subscribe('test_realtime')
    io_loop = tornado.ioloop.IOLoop.instance()
    for message in ps.listen():
        for element in LISTENERS:
            io_loop.add_callback(partial(element.on_message, message))