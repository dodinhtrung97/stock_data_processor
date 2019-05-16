import logging
import time

from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
from datetime import datetime
from ..utils.price_date import *
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

    def __init__(self, ticker_symbols, period=3):
        self.ticker_symbols = [ticker_symbol.upper() for ticker_symbol in ticker_symbols]
        self.period = period

    def validate_inputs(self):
        """
        Validates the inputs to Collector
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
        self.LOGGER.info("Clean data")
        # Remove rows that contain NaN values
        df = df.dropna()
        # Get necessary columns: [open, close, high, low, volume]
        df.columns = map(str.lower, df)
        necessary_columns = ['open', 'high', 'low', 'close', 'volume']
        if set(necessary_columns).issubset(set(df.columns.to_list())):
            df = df[necessary_columns]
        else:
            raise ValueError("There are not enough necessary columns from dataFrame")

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
        df = None
        ticker_symbol = ticker_symbol.upper()
        try:
            if start is not None:
                self.LOGGER.info("Collect data for {} from {}".format(ticker_symbol, start))
                df = get_historical_data(ticker_symbol, start=start, end=datetime.now(), output_format='pandas')
            else:
                self.LOGGER.info("Collect data for {} for {} year(s)".format(ticker_symbol, self.period))
                df = get_historical_data(ticker_symbol, start=(datetime.now() - relativedelta(years=self.period)), end=datetime.now(), output_format='pandas')
        except:
            raise ValueError("Cannot get data for {} from data source online".format(ticker_symbol))
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
        df = None
        ticker_symbol = ticker_symbol.upper()
        DataCollector.LOGGER.info("Load data for {}".format(ticker_symbol))
        df = load_dataframe_from_csv(ticker_symbol)
        if df is not None:
            df.index = df['date']
            df = df.drop(['date'], 1)
            DataCollector.LOGGER.info("Load successfully")

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
        df = None
        ticker_symbol = ticker_symbol.upper()
        df = self.load_data_for_ticker(ticker_symbol)
        if df is not None:
            if not data_is_lastest(df):
                self.LOGGER.info("Update data for {}".format(ticker_symbol))
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
