import logging
import time
import json
import requests

from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
from datetime import datetime
from ..utils.price_date import *
from ..utils.data_io import *
from .data_loader import DataLoader
from requests.exceptions import ConnectionError
from ..utils.utils import get_collector_config

CONFIG = get_collector_config()

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

    def __init__(self, ticker_symbols, period=3, use_local_storage=False):
        self.ticker_symbols = [ticker_symbol.upper() for ticker_symbol in ticker_symbols]
        self.period = period
        self.use_local_storage = use_local_storage

    def validate_inputs(self):
        """
        Validate the inputs to Collector
        """
        if self.period < 1:
            raise ValueError("Parameter 'period' must be greater than 0")

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
        df = pd.DataFrame()

        if start is None:
            start = datetime.now() - relativedelta(years=self.period)

        url =  'https://api.tiingo.com/tiingo/daily/'+ticker_symbol+'/prices?startDate='+str(start)+'&token='+CONFIG["TOKEN"]["TIINGO_TOKEN"]

        self.LOGGER.debug("Collecting data for {} for {} year(s)".format(ticker_symbol, self.period))
        
        try:
            response = requests.get(url)
            
            if response.ok: 
                bytes_data = response.content
                str_data =str(bytes_data,'utf-8')
                json_data = json.loads(str_data)
                df = pd.DataFrame.from_dict(json_data, orient='columns')

                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                    df.index = df['date']
                    df = df[['open', 'high', 'low', 'close', 'volume']]

                    self.LOGGER.debug("Collect successfully!")

        except ConnectionError as e:
            raise Exception("Failed to retrieve data for ticker {} from iexfinance, please check your internet connection. Exception follows. {}".format(ticker_symbol, e))
        
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
        save_dataframe_to_csv(df, ticker_symbol, use_local_storage=self.use_local_storage)

    def append_data_for_ticker(self, df, ticker_symbol):
        """
        Append data for ticker
            
        Parameters
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.
        """
        ticker_symbol = ticker_symbol.upper()
        append_dataframe_to_csv(df, ticker_symbol, use_local_storage=self.use_local_storage)

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
        df = DataLoader(ticker_symbol=ticker_symbol,
                        use_local_storage=self.use_local_storage).load_df()

        if not df.empty:
            if not data_is_lastest(df):
                self.LOGGER.debug("Updating data for {}".format(ticker_symbol))

                start = pd.to_datetime(df.tail(1).index.values[0]).date() + relativedelta(days=1)
                df_more = self.collect_data_for_ticker(ticker_symbol, start=start)
                self.append_data_for_ticker(df_more, ticker_symbol)
        else:
            df = self.collect_data_for_ticker(ticker_symbol, start=None)
            self.save_data_for_ticker(df, ticker_symbol)

        self.LOGGER.info("Collected and updated data for {}".format(ticker_symbol))

    def run(self):
        """
        Update data for tickers
        """
        self.validate_inputs()

        if self.ticker_symbols:
            for _, ticker_symbol in enumerate(self.ticker_symbols):
                self.update_data_for_ticker(ticker_symbol)
