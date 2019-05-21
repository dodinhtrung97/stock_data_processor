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
    setup_logging_with_config('logging.yaml')

    APP = Flask(__name__)
    SERVER_CONFIG = get_server_config()
    LOGGER = logging.getLogger(__name__)
    
    def __init__(self, args):
        self.start_websocket = bool(args.websocket)
        self.start_scrapper_controller = bool(args.scrapper)
        self.start_pattern_matcher_controller = bool(args.matcher)
        self.start_predictor_controller = bool(args.predictor)
        self.start_collector_controller = bool(args.collector)
        self.logging = bool(args.logging)

        self.__controller_dict = {}
        self.__service_dict = {}

        # Build controller dict
        self.controller_dict_init()
        # Build service dict
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
            controller_name = self.__controller_dict[controller]['controller']
            url_prefix = self.__controller_dict[controller]['url_prefix']

            self.APP.register_blueprint(controller_name, url_prefix=url_prefix)

        self.APP.run(host=self.SERVER_CONFIG['SERVER']['HOST'], 
                     port=self.SERVER_CONFIG['SERVER']['PORT'], 
                     threaded=True,
                     debug=False)

    def start_websocket_server(self):
        """
        Start Websocket Server
        """
        ws_ip = self.SERVER_CONFIG['WEBSOCKET_SERVER']['HOST']
        ws_route = self.SERVER_CONFIG['WEBSOCKET_SERVER']['ROUTE']
        ws_port = self.SERVER_CONFIG['WEBSOCKET_SERVER']['PORT']

        application = WSServer([(ws_route, WSHandler)])
        application.listen(ws_port)

        self.LOGGER.info('Websocket Server Started at ws://{}:{}{}'.format(ws_ip, ws_port, ws_route))
        scrapper_thread = threading.Thread(target=application.scrape, args=[self.logging])
        tornado_thread = threading.Thread(target=tornado.ioloop.IOLoop.instance().start)
        
        scrapper_thread.start()
        tornado_thread.start()

    def controller_dict_init(self): 
        """
        Initialize a controller dictionary that determines what blueprints will be registered into Flask Server
        Please only import controller modules within this function
        """
        self.LOGGER.info("Setting Up Server Environment ...")

        from web_scrapper.controller.scrapper_controller import scrapper_controller
        from pattern_matcher.controller.pattern_matcher_controller import pattern_matcher_controller
        from price_predictor.controller.predictor_controller import predictor_controller
        from data_collector.controller.collector_controller import collector_controller

        # Ignore 1st element of locals() 'self'
        controller_dict = dict.fromkeys([key for key in locals() if key != 'self'], dict())
        
        # Load data into config dictionary
        for index, controller_name in enumerate(controller_dict.copy()):
            is_activate_controller = getattr(self, 'start_{}'.format(controller_name))

            if is_activate_controller:
                controller_dict[controller_name] = {'controller': locals()[controller_name],
                                                    'url_prefix': self.SERVER_CONFIG['SERVER']['{}_{}'.format(controller_name.upper(), 'URL_PREFIX')]}
            else:
                controller_dict.pop(controller_name, None)

        self.__controller_dict = controller_dict

    def service_dict_init(self):
        """
        Initialize a service dictionary that determines what services will be ran
        """
        self.__service_dict = {
            'websocket': {
                'operation': self.start_websocket_server,
                'args': [],
                'activate': self.start_websocket,
                'threaded': False
            },
            'api': {
                'operation': self.start_api_server,
                'args': [],
                'activate': len(self.__controller_dict) > 0,
                'threaded': True
            }
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trade Advisor')
    parser.add_argument('--websocket', metavar='WEBSOCKET', default=1, type=int, help='Determine if websocket for auto_scraper module will be started')
    parser.add_argument('--scrapper', metavar='SCRAPPER', default=1, type=int, help='Determine if scraper module will be started')
    parser.add_argument('--matcher', metavar='MATCHER', default=1, type=int, help='Determine if pattern matcher module will be started')
    parser.add_argument('--predictor', metavar='PREDICTOR', default=1, type=int, help='Determine if predictor module will be started')
    parser.add_argument('--collector', metavar='COLLECTOR', default=1, type=int, help='Determine if collector module will be started')
    parser.add_argument('--logging', metavar='LOGGING', default=0, type=int, help='Log scrapping outputs into logs/*.json')
    args = parser.parse_args()

    # Start service
    backendServer(args).start()