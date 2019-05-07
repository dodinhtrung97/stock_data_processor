from flask import Flask
import argparse

import socket
import tornado
import threading

from web_scrapper.utils.utils import *
from web_scrapper.scrapper.scrapper import scrapper
from web_scrapper.websocket.ws_server import *

class backendServer():
    
    # Setup logging config
    setup_logging()

    APP = Flask(__name__)
    CONFIG = get_scrapper_config()
    LOGGER = logging.getLogger(__name__)
    
    def __init__(self, args):
        self.__start_websocket = bool(args.websocket)
        self.__start_scraper = bool(args.scraper)
        self.__start_matcher = bool(args.matcher)
        self.__logging = bool(args.logging)

        self.__controller_dict = {}
        self.__service_dict = {}

        # Build controller dict
        self.controller_dict_init()
        self.service_dict_init()

    def start(self):
        """
        Start main server
        """
        service_threadpool = []
        
        for service in self.__service_dict:
            if self.__service_dict[service]['activate'] and self.__service_dict[service]['threaded']:
                service_thread = threading.Thread(target=self.__service_dict[service]['operation'])
                service_threadpool.append(service_thread)

            elif self.__service_dict[service]['activate']:
                service = self.__service_dict[service]['operation']
                service()

        for threaded_service in service_threadpool:
            threaded_service.start()

    def start_api_server(self):
        """
        Register blueprints based on input command line args
        Start Flask Server
        """
        for controller in self.__controller_dict:
            if self.__controller_dict[controller]['activate']:
                controller_name = self.__controller_dict[controller]['controller']
                url_prefix = self.__controller_dict[controller]['url_prefix']

                self.APP.register_blueprint(controller_name, url_prefix=url_prefix)

        self.APP.run(host=self.CONFIG['SERVER']['HOST'], 
                     port=self.CONFIG['SERVER']['PORT'], 
                     threaded=True,
                     debug=False)

    def start_websocket_server(self):
        """
        Start Websocket Server
        """
        ws_ip = self.CONFIG['WEBSOCKET_SERVER']['HOST']
        ws_route = self.CONFIG['WEBSOCKET_SERVER']['ROUTE']
        ws_port = self.CONFIG['WEBSOCKET_SERVER']['PORT']

        application = WSServer([(ws_route, WSHandler)])
        application.listen(ws_port)

        self.LOGGER.info('Websocket Server Started at ws://{}:{}{}'.format(ws_ip, ws_port, ws_route))
        scrapper_thread = threading.Thread(target=application.scrape, args=[self.__logging])
        tornado_thread = threading.Thread(target=tornado.ioloop.IOLoop.instance().start)
        
        scrapper_thread.start()
        tornado_thread.start()

    def service_dict_init(self):
        """
        Initialize a service dictionary that determines what services will be ran
        """
        self.__service_dict = {
            'websocket': {
                'operation': self.start_websocket_server,
                'args': [],
                'activate': self.__start_websocket,
                'threaded': False
            },
            'api': {
                'operation': self.start_api_server,
                'args': [],
                'activate': self.__start_scraper or self.__start_matcher,
                'threaded': True
            }
        }

    def controller_dict_init(self): 
        """
        Initialize a controller dictionary that determines what blueprints will be registered into Flask Server
        """
        self.LOGGER.info("Setting Up Server Environment ...")

        from web_scrapper.controller.scrapper_controller import scrapper_controller
        from pattern_matcher.controller.pattern_matcher_controller import pattern_matcher_controller

        self.__controller_dict = {
            'scrapper_controller': {
                'controller': scrapper_controller,
                'url_prefix': self.CONFIG['SERVER']['SCRAPER_URL_PREFIX'],
                'activate': self.__start_scraper
            },
            'matcher_controller': {
                'controller': pattern_matcher_controller,
                'url_prefix': self.CONFIG['SERVER']['MATCHER_URL_PREFIX'],
                'activate': self.__start_matcher
            }
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trade Advisor')
    parser.add_argument('--websocket', metavar='WEBSOCKET', default=1, type=int, help='Determine if websocket for auto_scraper module will be started')
    parser.add_argument('--scraper', metavar='SCRAPPER', default=1, type=int, help='Determine if scraper module will be started')
    parser.add_argument('--matcher', metavar='MATCHER', default=1, type=int, help='Determine if pattern matcher module will be started')
    parser.add_argument('--logging', metavar='LOGGING', default=0, type=int, help='Log scrapping outputs into logs/*.json')
    args = parser.parse_args()

    # Start service
    backendServer(args).start()