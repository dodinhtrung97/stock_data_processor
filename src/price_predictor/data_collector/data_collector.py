import logging
import fix_yahoo_finance as yf

from datetime import datetime
from ..utils.price_date import get_lastest_price_day
from ..utils.data_io import *

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
        Get data from local
        If data is not available or out-of-date:
        1. Collecting original dataFrame from data source
        2. Clean data
        3. Store data
        """
        self.validate_inputs()
        lastest_price_day = get_lastest_price_day()
        file_name = self.ticker_symbol

        try:
            # Get data from local
            self.LOGGER.info("Loading data for {} with period {} from local".format(self.ticker_symbol, self.period))
            self.results = load_dataframe_from_csv(file_name)
            self.results.index = self.results['Date']
            self.results = self.results.drop(['Date'], 1)
            # Check data in local is lastest
            if pd.to_datetime(self.results.tail(1).index.values[0]).date() != lastest_price_day:
                self.LOGGER.info("Data of ticker {} from local is not lastest".format(self.ticker_symbol))
                raise ValueError("Data from local is not lastest")
        except:
            try:
                # Get data online
                self.LOGGER.info("Collecting data for {} with period {} online".format(self.ticker_symbol, self.period))
                ticker = yf.Ticker(self.ticker_symbol)
                self.results = ticker.history(period = str(self.period) + "y")
                # Check data from online is lastest
                if pd.to_datetime(self.results.tail(1).index.values[0]).date() == lastest_price_day:
                    self.clean_data()
                    save_dataframe_to_csv(self.results, file_name)
                else:
                    self.LOGGER.info("Data of ticker {} from online is not lastest".format(self.ticker_symbol))
                    raise ValueError("Data from data source is not lastest")
            except:
                raise ValueError("Cannot get data from data source online")

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





    




