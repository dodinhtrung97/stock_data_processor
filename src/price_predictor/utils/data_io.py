import pandas as pd
import os
import errno

from .utils import get_predictor_config

CONFIG = get_predictor_config()

def save_dataframe_to_csv(df, file_name):    
    file_path = os.path.join(CONFIG['PREDICTOR']['DIR_DATA'], file_name)
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise ValueError("Cannot make directory {}".format(os.path.dirname(file_path)))
    
    try:
        df.to_csv(file_path)
    except:
        raise ValueError("Cannot save dataframe to {}.csv".format(file_path))

def load_dataframe_from_csv(file_name):
    df = None
    try:
        df = pd.read_csv(os.path.join(CONFIG['PREDICTOR']['DIR_DATA'], file_name))
    except:
        raise ValueError("Cannot load dataframe from {}.csv".format(file_name))

    return df

    