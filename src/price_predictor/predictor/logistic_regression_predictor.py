import numpy as np
import logging
import pandas as pd
import os

from sklearn import preprocessing
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error
from datetime import datetime
from dateutil.relativedelta import relativedelta
from data_collector.utils.price_date import get_future_day
from ..utils.utils import get_predictor_config

class LogisticRegPredictor:
    """
    Logistic Regression Predictor

    Parameters
    ----------
    period (Integer): Period for collecting data from past to now (number of years)
    df (pd.DataFrame): DataFrame from Data Collector
    features (list): List names of column in dataFrame that used for prediction
    target (list): Name of column in dataFrame that needed to predict
    model (object): Type model for training and prediction
    confidence (float): Confidence of model after training (in range [0, 1])
    error (float): Mean absolute error in test dataset
    results (dictionary): Predictive values in forecast_days {key (datetime): predictive value}
    """

    LOGGER = logging.getLogger(__name__)
    CONFIG = get_predictor_config()

    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol
        self.forecast_days = 1

        self.df = pd.DataFrame()
        self.features = ["open", "close", "high", "low", "volume"]
        self.accuracy = None
        self.precision = None
        self.recall = None
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
                raise ValueError("Feature columns must exist in DataFrame")

    def load_data(self):
        """
        Load ticker data
        """
        self.ticker_symbol = self.ticker_symbol.upper()
        self.LOGGER.debug("Loading data for ticker {}".format(self.ticker_symbol))

        file_path = os.path.join(self.CONFIG["PREDICTOR"]["STORAGE"], self.ticker_symbol)

        if os.path.exists(file_path):
            try:
                self.df = pd.read_csv(file_path)
            except IOError as e:
                raise Exception("Failed to load dataframe from {}.csv. Exception follows. {}".format(self.ticker_symbol, e))

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
        self.load_data()

        if self.df.empty:
            self.LOGGER.error("Failed to predict stock trend. Exception follows. Empty data frame, check if designated data folder exists")
            raise Exception("Failed to predict stock trend. Exception follows. Empty data frame, check if designated data folder exists")

        self.LOGGER.debug("Predicting stock trend for ticker {}".format(self.ticker_symbol))

        x = self.df[self.features]
        y = np.where(x['close'] > x['close'].shift(-1), 1, -1)

        test_size = 0.2
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=0)

        model = LogisticRegression()
        model.fit(x_train, y_train)

        y_test_predict = model.predict(x_test)

        self.accuracy = metrics.accuracy_score(y_test, y_test_predict)
        self.precision = metrics.precision_score(y_test, y_test_predict)
        self.recall = metrics.recall_score(y_test, y_test_predict)

        y_predicted = model.predict(x.tail(1))
        future_day = get_future_day(self.forecast_days)

        self.results = {'date': future_day[0],
                        'trend': int(y_predicted[0]),
                        'accuracy': self.accuracy,
                        'precision': self.precision,
                        'recall': self.recall}
