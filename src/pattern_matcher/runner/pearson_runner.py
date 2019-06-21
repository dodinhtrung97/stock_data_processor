from ..runner.runner import Runner
from ..measurements.pearson import Pearson
from ..processor.processor import MultiProcessingMeasurementProcessor, MultiThreadingMeasurementProcessor
from ..measurements.measurement import Measurement
from ..matcher.matcher import PearsonMatcher
from ..loader import csv_loader as loader
from ..processor.job import Job
import time
import logging

class PearsonRunner(Runner):

    def __init__(self, conf, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        if conf['measurement']['multiprocessing'] is True:
            self.__processor = MultiProcessingMeasurementProcessor()
        elif conf['measurement']['threading'] is True:
            self.__processor = MultiThreadingMeasurementProcessor()
        else:
            raise Exception('Unable to read conf for processor type')
        Runner.__init__(self, conf, self.logger)
        self.__matcher = PearsonMatcher()

    def run(self, ticker, days_back, days_forward, top):
        self.logger.info('Run pattern matching with ticker: %s - measurement: %s', ticker, self.__matcher)
        if ticker not in self._TICKERS:
            self.logger.info('Unsupported ticker exception: %s', ticker)
            raise NameError('Failed to find ticker: {0}. Please provide the correct ticker'.format(ticker))

        # load pattern data
        pattern_dataframe = self._CACHE_DATA[ticker]
        pattern_size = len(pattern_dataframe)
        pattern_date = pattern_dataframe.iloc[pattern_size - days_back:pattern_size, 0].values
        pattern_date_values = [pattern_date[1], pattern_date[-1]]
        pattern_close_values = pattern_dataframe.iloc[pattern_size - days_back:pattern_size, 1].to_list()

        # create measurement job
        job_name = 'spearman-' + ticker + '-' + str(time.time())
        spearman_meas_job = Job(job_name, self.__matcher.match, pattern_close_values, days_forward, 1)

        # conduct a process
        results = self.__processor.process(self._CACHE_DATA, spearman_meas_job, self._CONCURRENCY)

        # sort the results by ascending
        results.sort(key = lambda x: x[1], reverse=True)

        # take the top results
        top_results = results[:top]

        #return results
        return self.convert_to_json(ticker, pattern_close_values, pattern_date_values, top_results)