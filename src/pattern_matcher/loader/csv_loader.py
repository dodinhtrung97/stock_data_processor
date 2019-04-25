import pandas as pd
import numpy as np

def load(file_path, delimiter = ',', usecols=None):
    return pd.read_csv(file_path, delimiter=delimiter, usecols=usecols)
