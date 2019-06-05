import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.options
 
import time
import json
import uuid
import logging
import os
import configparser

from ..scrapper.automated_scrapper import automatedScrapper
from ..utils.utils import get_scrapper_config 

CONFIG = get_scrapper_config()
LOGGER = logging.getLogger(__name__)

automated_scrapper = automatedScrapper()

ticker_symbol_set = set()
clients_address = {}
client_portfolios = {}
 
class WSServer(tornado.web.Application):

    def scrape(self, logging=False):
        sleep_time_s = int(CONFIG['SCRAPPER']['SLEEP_TIME'])

        while True:
            # Pending if no works
            if not len(client_portfolios) > 0:
                time.sleep(1)
                continue

            automated_scrapper.set_ticker_symbol(ticker_symbol_set.copy())
            result = automated_scrapper.run(logging=logging)
            
            for ticker in result.keys():
                if not len(result[ticker]) > 0: 
                    response = {
                                ticker: {
                                    "DUMMY_SOURCE": [
                                      {
                                        "url": "https://doesnt.exist.com",
                                        "headline": "Dummy Headline",
                                        "date": 0.0,
                                        "direct": False,
                                        "score": "0"
                                      },
                                    ]}
                                }
                else:
                    response = json.dumps({ticker: result[ticker]})
    
                try: [clients_address[client].write_message(response) for client in client_portfolios[ticker]]
                except KeyError as e:   
                    LOGGER.info("No subscribers for {}, ignoring scrapped news...".format(ticker))

            LOGGER.info("Scrapping finished, sleeping for {}s".format(sleep_time_s))
            time.sleep(sleep_time_s)
 
class WSHandler(tornado.websocket.WebSocketHandler):
 
    def __init__(self, application, request, **kwargs):
        super(WSHandler, self).__init__(application, request, **kwargs)
        self.client_id = str(uuid.uuid4())
 
    def open(self):
        clients_address[self.client_id] = self
 
        LOGGER.info("Connection from {} accepted".format(self.client_id))
        self.write_message(json.dumps({'action': 'connect',
                                       'status': 'Success',
                                       'value': self.client_id}))
      
    def on_message(self, message):
        """
        Deals with user requested action
        Request json must strictly be in the form of
        Request: { "action" : <String>, 
                   "value": <String> }
        Where actions could be one of <add_ticker, remove_ticker>
        Eg:      { "action" : "add_ticker", 
                   "value" : "aapl"} 
        """
        message = json.loads(message)
        action = message['action']
        value = message['value'].strip()

        if value == '': 
            self.write_message(json.dumps({'action': 'add_ticker',
                                           'status': 'Failure',
                                           'value': value}))
            return

        if action == 'add_ticker':
            try:
                self.add_ticker_subscriber(client_id=self.client_id, ticker=value)
                self.write_message(json.dumps({'action': 'add_ticker',
                                               'status': 'Success',
                                               'value': value}))
            except KeyError as e:
                self.write_message(json.dumps({'action': 'add_ticker',
                                               'status': 'Success',
                                               'value': value}))

            except Exception as e:
                self.write_message(json.dumps({'action': 'add_ticker',
                                               'status': 'Failure',
                                               'value': value}))
        if action == 'remove_ticker':
            try:
                self.remove_ticker_subscriber(client_id=self.client_id, ticker=value)
                self.write_message(json.dumps({'action': 'remove_ticker',
                                               'status': 'Success',
                                               'value': value}))
            except KeyError as e:
                self.write_message(json.dumps({'action': 'remove_ticker',
                                               'status': 'Failure',
                                               'value': value}))
 
    def on_close(self):
        # Remove from all subscriber lists 
        for ticker in client_portfolios.copy():
            self.remove_ticker_subscriber(ticker, self.client_id)
        # Remove from known clients_address
        clients_address.pop(self.client_id, None)
        LOGGER.info('Connection with {} terminated...'.format(self.client_id))
 
    def check_origin(self, origin):
        return True
 
    def remove_ticker_subscriber(self, ticker, client_id):
        """
        Remove client id from subscriber list of input ticker
        
        Args:
            ticker (TYPE): Description
            client_id (TYPE): Description
        """
        ticker = ticker.upper()
        try:
            subscribers_set = client_portfolios[ticker]

            # Remove user from subscriber list
            if client_id in subscribers_set:
                subscribers_set.remove(client_id)
                client_portfolios[ticker] = subscribers_set
                LOGGER.info('Removed client {} from {} subscribers list'.format(self.client_id, ticker))

            # Remove ticker from scrapping queue if no subscribers
            if not len(client_portfolios[ticker]) > 0:
                client_portfolios.pop(ticker, None)
                ticker_symbol_set.remove(ticker)
                LOGGER.info('No subscribers for ticker {}. Removed from scrapping queue'.format(ticker))
 
        except KeyError as e:
            LOGGER.error('Ticker {} is not in scrapping queue. Failed to remove binding for user {}'.format(ticker, client_id))
            raise KeyError
 
    def add_ticker_subscriber(self, ticker, client_id):
        """
        Add client_id to subscriber list of input ticker
        
        Args:
            client_id (TYPE): Description
            ticker (TYPE): Description
        """
        ticker = ticker.upper()
        try:
            client_portfolios[ticker].add(client_id)
            LOGGER.info("Added {} to list of {} subscribers".format(client_id, ticker))
 
        except KeyError as e:
            client_portfolios[ticker] = {client_id}
            ticker_symbol_set.add(ticker)
            LOGGER.info("List of {} subscribers not yet exists. Added to queue for next scrapping session".format(ticker))
            LOGGER.info("Added {} to list of {} subscribers".format(client_id, ticker))
            raise KeyError
 
        except Exception as e:
            LOGGER.info("Failed to add {} to list of {} subscribers. Exception follows {}".format(client_id, ticker, e))
            raise Exception