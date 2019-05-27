import numpy as np
import logging
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from fbprophet import Prophet
from data_collector.utils.price_date import get_future_day

class ProphetPredictor:
    """
    Prophet Predictor

    Parameters
    ----------
    period (Integer): Period for collecting data from past to now (number of years)
    df (pd.DataFrame): DataFrame from Data Collector
    forecast_days (Integer): Number of ahead days for forcasting
    model (object): Type model for training and prediction
    results (dictionary): Predictive values in forecast_days {key (datetime): predictive value}
    """

    LOGGER = logging.getLogger(__name__)

    def __init__(self, df, forecast_days):
        self.df = df
        self.df["ds"] = self.df.index
        self.df["y"] = self.df['close']
        self.df = self.df[["ds", "y"]]

        self.forecast_days = forecast_days
        self.model = Prophet()
        self.results = None

        self.validate_inputs()

    def validate_inputs(self):
        """
        Validates the inputs to Prophet Predictor
        """
        if self.forecast_days < 1:
            raise ValueError("Parameter 'forecast_days' must be greater than 0")

    def run(self):
        """
        Train model
        Give results of predictor
        """
        if not self.df.empty:
            self.model.fit(self.df)
            future_days = get_future_day(self.forecast_days)
            
            df_forecast = pd.DataFrame({"ds": [datetime.fromtimestamp(day).date() for day in future_days]})
            df_result = self.model.predict(df_forecast)

            self.results = dict(zip(future_days, df_result["yhat"]))
