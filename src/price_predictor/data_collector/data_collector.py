import logging
import fix_yahoo_finance as yf

from datetime import datetime

class DataCollector:
    """
    Data Collector

    Parameters
    ----------
    ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.
    period (Integer): Period for collecting data from past to now (number of years)
    results (pd.DataFrame): DataFrame from data source
    """

    LOGGER = logging.getLogger(__name__)

    def __init__(self, ticker_symbol, period=5):
        self.ticker_symbol = ticker_symbol.upper()
        self.period = period

        self.results = None

    def validate_inputs(self):
        """
        Validates the inputs to Collector
        """
        if self.period < 1:
            raise ValueError("Parameter 'period' must be greater than 0")

    def collect(self):
        """
        Start collecting original dataFrame from data source
        """
        self.validate_inputs()
        ticker = yf.Ticker(self.ticker_symbol)
        try:
            self.LOGGER.info("Collecting data for {} with period {}".format(self.ticker_symbol, self.period))
            self.results = ticker.history(period = str(self.period) + "y")
        except:
            raise ValueError("Cannot get data from data source")

    def clean_data(self):
        """
        Clean data in dataframe before using for training model or predicting
        """
        self.LOGGER.info("Cleaning data for ticker {}".format(self.ticker_symbol))

        # Remove rows that contain NaN values
        self.results = self.results.dropna()

        # Get necessary columns: [open, close, high, low, volume]
        self.results.columns = map(str.lower, self.results)
        necessary_columns = ['open', 'high', 'low', 'close', 'volume']
        if set(necessary_columns).issubset(set(self.results.columns.to_list())):
            self.results = self.results[necessary_columns]
        else:
            raise ValueError("There are not enough necessary columns from dataFrame")

    def run(self):
        """
        All processes in collecting
        """
        self.collect()
        self.clean_data()







    




