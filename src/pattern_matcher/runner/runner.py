import time, sys, os
import logging
import glob
import numpy as np
from ..loader import csv_loader as loader

class Runner():
    
    _CACHE_DATA = dict()
    _DATA_PATH = None
    _TICKERS = None
    _FORMAT = None
    _CONCURRENCY = os.cpu_count()

    def __init__(self, conf, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.conf = conf
        self.init_runner(self.conf)
        self.get_all_tickers()
        self.load_data()

    def get_all_tickers(self):
        files = [f for f in glob.glob(self._DATA_PATH + '/*' + self._FORMAT, recursive=False)]
        self._TICKERS = [os.path.splitext(os.path.basename(file))[0].split('.')[0] for file in files]
    
    def init_runner(self, conf):
        if conf['input']['dir'] and conf['input']['format']:
            self._DATA_PATH = conf['input']['dir']
            self._FORMAT =  conf['input']['format']
            self._CONCURRENCY = int(conf['measurement']['concurrency'])
        else:
            raise Exception('Unable to read conf: {}'.format('input'))

    def run(self, ticker, days_back, days_forward, top):
        pass

    def convert_to_json(self, ticker, pattern_close_values, pattern_date_values, predict):
        # Initilize origin
        origin = {
            'ticker': ticker,
            'values': pattern_close_values,
            'time': pattern_date_values
        }
        # Initilize matches
        matches, i = {}, 1
        for item in predict:
            matches[i] = {
                'ticker': item[0],
                'similarity': item[1],
                'history': item[2][0],
                'time': item[2][1],
                'future': item[2][2]
            }
            i += 1
        return {
            'origin': origin,
            'matches': matches
        }

    def load_data(self):
        self.logger.info('Loading stock data ...')
        # self._CACHE_DATA = {ticker: loader.load(self._DATA_PATH + '/' + ticker + self._FORMAT, delimiter=',', usecols=['Date', 'Close']) for ticker in self._TICKERS}
        for ticker in self._TICKERS:
            try:
                self._CACHE_DATA[ticker] = loader.load(self._DATA_PATH + '/' + ticker + self._FORMAT, delimiter=',', usecols=['Date', 'Close'])
            except Exception as e:
                self.logger.error('Failed to load data with ticker: %s. Exception follows. %s', ticker, e)
                raise Exception('Failed to load data: {0}. Exception follows. {1}'.format(ticker, e))