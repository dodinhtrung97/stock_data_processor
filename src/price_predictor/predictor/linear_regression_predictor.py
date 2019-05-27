import numpy as np
import logging
import pandas as pd
import os

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from datetime import datetime
from dateutil.relativedelta import relativedelta
from data_collector.utils.price_date import get_future_day
from ..utils.utils import get_predictor_config

CONFIG = get_predictor_config()

class LinearRegPredictor:
    """
    Linear Regression Predictor

    Parameters
    ----------
    period (Integer): Period for collecting data from past to now (number of years)
    df (pd.DataFrame): DataFrame from Data Collector
    features (list): List names of column in dataFrame that used for prediction
    target (list): Name of column in dataFrame that needed to predict
    forecast_days (Integer): Number of ahead days for forcasting
    model (object): Type model for training and prediction
    confidence (float): Confidence of model after training (in range [0, 1])
    error (float): Mean absolute error in test dataset
    results (dictionary): Predictive values in forecast_days {key (datetime): predictive value}
    """

    LOGGER = logging.getLogger(__name__)

    def __init__(self, ticker_symbol, forecast_days):
        self.ticker_symbol = ticker_symbol
        self.forecast_days = forecast_days

        self.df = pd.DataFrame()
        self.features = ["open", "close", "high", "low", "volume"]
        self.target = ["close"]
        self.model = LinearRegression()
        self.confidence = None
        self.error = None
        self.results = None
        self.validate_inputs()

    def validate_inputs(self):
        """
        Validates the inputs to Linear Regression Predictor
        """
        if self.forecast_days < 1:
            raise ValueError("Parameter 'forecast_days' must be greater than 0")

        if not self.df.empty:
            if not set(self.features).issubset(self.df.columns.to_list()):
                raise ValueError("Feature columns must be exist in DataFrame")

            if not set(self.target).issubset(self.df.columns.to_list()):
                raise ValueError("Target columns must be exist in DataFrame")

    def load_data_for_ticker(self):
        """
        Load data for ticker
            
        Parameters
        ----------
        ticker_symbol (String): Stock code, eg: AAPL for Apple Inc.

        Returns
        ----------
        df (DataFrame): Columns['open', 'high', 'low', 'close', 'volume'], index['date']
        """
        self.ticker_symbol = self.ticker_symbol.upper()
        self.LOGGER.debug("Loading data for {}".format(self.ticker_symbol))

        file_path = os.path.join(CONFIG["PREDICTOR"]["STORAGE"], self.ticker_symbol)

        if os.path.exists(file_path):
            try:
                self.df = pd.read_csv(file_path)
            except IOError as e:
                raise Exception("Cannot load dataframe from {}.csv. Exception follows. {}".format(self.ticker_symbol, e))

        if not self.df.empty:
            self.df.index = self.df['date']
            self.df = self.df.drop(['date'], 1)
            self.LOGGER.debug("Load successfully")

    def run(self):
        """
        Split training & test dataset for model
        Train model
        Calculate metrics to evaluate performance of model
        Give results of predictor
        """
        self.load_data_for_ticker()

        if not self.df.empty:
            self.LOGGER.debug("Predicting")
            self.df['target'] = self.df[self.target].shift(-self.forecast_days)

            # X: feature dataset
            X = np.array(self.df[self.features])
            X = preprocessing.scale(X)
            # Get features of lastest forecast_days for predicting
            X_forecast = X[-self.forecast_days:]
            X = X[:-self.forecast_days]
            # y: target dataset
            y = np.array(self.df['target'])
            y = y[:-self.forecast_days]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)

            # Testing, calculating Coefficient and Error of model
            self.confidence = self.model.score(X_test, y_test)
            self.error = mean_absolute_error(y_test, self.model.predict(X_test))

            # Creating results as dictionary {key (datetime): predicted value}
            predictive_values = self.model.predict(X_forecast)
            future_days = get_future_day(self.forecast_days)
            self.results = dict(zip(future_days, predictive_values.tolist()))
