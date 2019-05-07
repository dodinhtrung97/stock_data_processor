import numpy as np
import logging

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

    def __init__(self, df, forecast_days):
        self.df = df
        self.forecast_days = forecast_days

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

        if not set(self.features).issubset(self.df.columns.to_list()):
            raise ValueError("Feature columns must be exist in DataFrame")

        if not set(self.target).issubset(self.df.columns.to_list()):
            raise ValueError("Target columns must be exist in DataFrame")

    def run(self):
        """
        Spliting tranining & test dataset for model
        Training model
        Calculating metrics to evaluate performance of model
        Give results of predictor
        """
        self.LOGGER.info("Predicting for ticker")
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
        dates = [(datetime.now() + relativedelta(days = i)).timestamp() for i in range(self.forecast_days)]
        self.results = dict(zip(dates, predictive_values.tolist()))

    