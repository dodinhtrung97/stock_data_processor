import logging
import time

from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
from datetime import datetime
from ..utils.price_date import *
from ..utils.data_io import *
from requests.exceptions import ConnectionError

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

    def __init__(self, ticker_symbols, period=3):
        self.ticker_symbols = [ticker_symbol.upper() for ticker_symbol in ticker_symbols]
        self.period = period

    def validate_inputs(self):
        """
        Validate the inputs to Collector
        """
        if self.period < 1:
            raise ValueError("Parameter 'period' must be greater than 0")

    def clean_data(self, df):
        """
        Clean data in dataframe before using for training model or predicting
            
        Parameters
        ----------
        df (DataFrame)

        Returns
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        """
        df = df.dropna()
        # Get necessary columns: [open, close, high, low, volume]
        df.columns = map(str.lower, df)
        necessary_columns = ['open', 'high', 'low', 'close', 'volume']

        if set(necessary_columns).issubset(set(df.columns.to_list())):
            df = df[necessary_columns]
        else:
            raise ValueError("Missing columns from dataFrame")

        return df

    def collect_data_for_ticker(self, ticker_symbol, start=None):
        """
        Collect data for ticker
            
        Parameters
        ----------
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.

        Returns
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        """
        ticker_symbol = ticker_symbol.upper()
        df = None
        
        try:
            if start:
                self.LOGGER.debug("Collecting data for {} from {}".format(ticker_symbol, start))
                df = get_historical_data(ticker_symbol, start=start, end=datetime.now(), output_format='pandas')
            else:
                self.LOGGER.debug("Collecting data for {} for {} year(s)".format(ticker_symbol, self.period))
                df = get_historical_data(ticker_symbol, start=(datetime.now() - relativedelta(years=self.period)), end=datetime.now(), output_format='pandas')
        except ConnectionError as e:
            raise Exception("Failed to retrieve data for ticker {} from iexfinance, please check your internet connection. Exception follows. {}".format(ticker_symbol, e))
        
        self.LOGGER.debug("Cleaning data for {}".format(ticker_symbol))

        df = self.clean_data(df)

        return df

    @classmethod
    def load_data_for_ticker(self, ticker_symbol):
        """
        Load data for ticker
            
        Parameters
        ----------
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.

        Returns
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        """
        ticker_symbol = ticker_symbol.upper()
        DataCollector.LOGGER.debug("Loading data for {}".format(ticker_symbol))

        df = None
        df = load_dataframe_from_csv(ticker_symbol)

        if df is not None:
            df.index = df['date']
            df = df.drop(['date'], 1)
            DataCollector.LOGGER.debug("Load successfully")

        return df

    def save_data_for_ticker(self, df, ticker_symbol):
        """
        Save data for ticker
            
        Parameters
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.
        """
        ticker_symbol = ticker_symbol.upper()
        save_dataframe_to_csv(df, ticker_symbol)

    def append_data_for_ticker(self, df, ticker_symbol):
        """
        Append data for ticker
            
        Parameters
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.
        """
        ticker_symbol = ticker_symbol.upper()
        append_dataframe_to_csv(df, ticker_symbol)

    def update_data_for_ticker(self, ticker_symbol):
        """
        Update data for ticker
        If data is available and data is not lastest, get more data
        If data is available, get data for period
        Store data (file .csv)

        Parameters
        ----------
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.
        """
        ticker_symbol = ticker_symbol.upper()
        df = None
        df = self.load_data_for_ticker(ticker_symbol)

        if df is not None:
            if not data_is_lastest(df):
                self.LOGGER.debug("Updating data for {}".format(ticker_symbol))

                start = pd.to_datetime(df.tail(1).index.values[0]).date() + relativedelta(days=1)
                df_more = self.collect_data_for_ticker(ticker_symbol, start=start)
                self.append_data_for_ticker(df_more, ticker_symbol)
        else:
            df = self.collect_data_for_ticker(ticker_symbol, start=None)
            self.save_data_for_ticker(df, ticker_symbol)

    def run(self):
        """
        Update data for tickers
        """
        self.validate_inputs()

        if self.ticker_symbols:
            for _, ticker_symbol in enumerate(self.ticker_symbols):
                self.update_data_for_ticker(ticker_symbol)
