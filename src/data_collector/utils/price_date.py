import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_lastest_price_day():
    """
    Get the lastest day when stock price data should be updated
    e.g.
    If today is Wednesday, the lastest data should have updated date which is Tuesday
    But with Sunday and Monday, the expected date is Friday

    Returns
    ----------
    lastest_price_date (Datetime.Date): The lastest day when stock price data should be updated, format YYYY-MM-DD
    e.g. Datetime.Date(2019-04-17)
    """
    delta_days = 1
    weekday = datetime.today().weekday()
    if weekday == 6:
        delta_days = 2
        
    if weekday == 0:
        delta_days = 3
        
    lastest_price_date = datetime.today() - relativedelta(days=delta_days)

    return lastest_price_date.date()

def data_is_lastest(df):
    """
    Check data is lastest or out-of-date

    Parameters
    ----------
    df (DataFrame)

    Returns
    ----------
    (Bool)
    """
    lastest_price_date = get_lastest_price_day()
    if pd.to_datetime(df.tail(1).index.values[0]).date() == lastest_price_date:
        return True
    return False
        