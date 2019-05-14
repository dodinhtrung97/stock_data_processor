import pandas as pd
import os
import errno

from .utils import get_collector_config

CONFIG = get_collector_config()

def save_dataframe_to_csv(df, file_name):
    """
    Save DataFrame to file with format csv

    Parameters
    ----------
    df (DataFrame)
    file_name (String): Name of file
    """    
    file_path = os.path.join(CONFIG["PREDICTOR"]["DIR_DATA"], file_name)
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise ValueError("Cannot make directory {}".format(os.path.dirname(file_path)))
    
    try:
        df.to_csv(file_path)
    except IOError as e:
        raise Exception("Cannot save dataframe to {}.csv. Exception follows. {}".format(file_path, e))

def load_dataframe_from_csv(file_name):
    """
    Load DataFrame from file csv

    Parameters
    ----------
    file_name (String): Name of file

    Returns
    ----------
    df (DataFrame)
    """    
    df = None

    file_path = os.path.join(CONFIG["PREDICTOR"]["DIR_DATA"], file_name)
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
        except IOError as e:
            raise Exception("Cannot load dataframe from {}.csv. Exception follows. {}".format(file_name, e))

    return df

def append_dataframe_to_csv(df, file_name):
    """
    Append DataFrame to file csv

    Parameters
    ----------
    df (DataFrame)
    file_name (String): Name of file
    """    
    file_path = os.path.join(CONFIG["PREDICTOR"]["DIR_DATA"], file_name)
    if os.path.exists(file_path):
        try:
            df.to_csv(file_path, mode='a', header=False)
        except IOError as e:
            raise Exception("Cannot append dataframe to {}.csv. Exception follows. {}".format(file_name, e))
