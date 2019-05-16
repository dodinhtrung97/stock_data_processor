import logging
import threading
import time

from ..collector.data_collector import DataCollector
from ..utils.utils import get_ticker_list

class Runner():
    """
    Manage to execute Data Collectors

    Parameters
    ----------
    tickers (List): list of ticker_symbol, eg: ["AMZN", "BKNG" ...]
    num_threads (Integer): number of threads, each thread runs a DataCollector
    data_collectors (List): list of (type) DataCollector
    """

    LOGGER = logging.getLogger(__name__)

    def __init__(self, num_threads=4):
        self.tickers = get_ticker_list()['tickers']
        self.num_threads = num_threads
        self.data_collectors = None

        self.validate_inputs()
        self.create_data_collectors()

    def validate_inputs(self):
        """
        Validates the inputs to Runner
        """
        if self.num_threads > len(self.tickers):
            raise ValueError("Parameter 'num_threads' must be not greater than number of ticker")

    def create_data_collectors(self):
        """
        Devide list ticker to many ticker bins
        Contruct DataCollector by ticker bin
        """
        ticker_bins = []
        for _ in range(self.num_threads):
            ticker_bins.append([])

        bin_idx = 0
        for _, ticker in enumerate(self.tickers):
            ticker_bins[bin_idx].append(ticker)
            bin_idx = bin_idx + 1
            if bin_idx == len(ticker_bins):
                bin_idx = 0

        self.data_collectors = [DataCollector(ticker_bin) for ticker_bin in ticker_bins]

    def run_data_colector(self, data_collector):
        """
        Execute a DataCollector

        Parameters
        ----------
        data_collector (DataCollector)
        """
        data_collector.run()

    def run(self):
        """
        Execute multi-threads in data collecting process
        """
        threads = []
        for _, data_collector in enumerate(self.data_collectors):
            thread = threading.Thread(target=self.run_data_colector, args=[data_collector,])
            threads.append(thread)

        for _, thread in enumerate(threads):
            thread.start()

        for _, thread in enumerate(threads):
            thread.join()
