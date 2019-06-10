import logging
import time

from dateutil.parser import *
from ..utils.data_io import *

class DataLoader:
    """
    Data Collector

    Parameters
    ----------
    ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.
    period (Integer): Period for collecting data from past to now (number of years)
    results (pd.DataFrame): DataFrame from data source
    """

    LOGGER = logging.getLogger(__name__)

    def __init__(self, ticker_symbol, period=3, use_local_storage=False):
        self.ticker_symbol = ticker_symbol.upper()
        self.period = period
        self.use_local_storage = use_local_storage

    def validate_inputs(self):
        """
        Validate the inputs to Collector
        """
        if self.period < 1:
            raise ValueError("Parameter 'period' must be greater than 0")

    def load_df(self):
        """
        Load data for ticker
            
        Parameters
        ----------
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.

        Returns
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        """
        self.LOGGER.debug("Loading data for {}".format(self.ticker_symbol))

        df = load_dataframe_from_csv(file_name=self.ticker_symbol, 
                                     use_local_storage=self.use_local_storage)

        if not df.empty:
            df.index = df['date']
            df = df.drop(['date'], 1)
            self.LOGGER.debug("Load successfully")

        return df
    
    def load_json_data(self):
        """
        Load json data for self.ticker
        """
        self.LOGGER.debug("Loading data for {}".format(self.ticker_symbol))

        df = load_dataframe_from_csv(file_name=self.ticker_symbol, 
                                     use_local_storage=self.use_local_storage)

        if df.empty:
            raise Exception("Data frame empty, check if data for {} exists in designated data directory".format(self.ticker_symbol))
       
        result_set = []
        for index, rows in df.iterrows():
            entry = {'date': parse(rows['date'], fuzzy=True).timestamp(),
                     'open': rows['open'],
                     'high': rows['high'],
                     'low': rows['low'],
                     'close': rows['close']}
            result_set.append(entry)

        return result_set
