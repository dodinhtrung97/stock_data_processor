from src import create_ws
import threading, logging
import socket, tornado

ws = create_ws()
LOGGER = logging.getLogger(__name__)

if __name__ == "__main__":
    
    ws_ip = '0.0.0.0'
    ws_route = '/news'
    ws_port = 10005

    LOGGER.info('Websocket Server Started at ws://{}:{}{}'.format(ws_ip, ws_port, ws_route))
    ws.listen(ws_port)
    scrapper_thread = threading.Thread(target=ws.scrape, args=[logging])
    tornado_thread = threading.Thread(target=tornado.ioloop.IOLoop.instance().start)
    
    scrapper_thread.start()
    tornado_thread.start()