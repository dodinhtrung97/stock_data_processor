import pandas as pd
import os
import errno
import logging
from shutil import copy
from .utils import get_collector_config

CONFIG = get_collector_config()
LOGGER = logging.getLogger(__name__)

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOCAL_STORAGE_PATH = os.path.join(DIR_PATH, '..', '..', '..', CONFIG["COLLECTOR"]["LOCAL_STORAGE"])
REMOTE_STORAGE_PATH = os.path.join(DIR_PATH, '..', '..', '..', CONFIG["COLLECTOR"]["REMOTE_STORAGE"])

def save_dataframe_to_csv(df, file_name, use_local_storage):
    """
    Save DataFrame to file with format csv

    Parameters
    ----------
    df (DataFrame)
    file_name (String): Name of file
    """   
    file_path = os.path.join(LOCAL_STORAGE_PATH, file_name)

    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise Exception("Cannot make directory {}".format(os.path.dirname(file_path), e))
    
    try:
        df.to_csv(file_path)
    except IOError as e:
        raise Exception("Cannot save dataframe to {}.csv. Exception follows. {}".format(file_path, e))

    if not use_local_storage:
        copy_local_file_to_remote_storage(file_name)

def append_dataframe_to_csv(df, file_name, use_local_storage):
    """
    Append DataFrame to file csv

    Parameters
    ----------
    df (DataFrame)
    file_name (String): Name of file
    """    
    file_path = os.path.join(LOCAL_STORAGE_PATH, file_name)
    
    if os.path.exists(file_path):
        try:
            df.to_csv(file_path, mode='a', header=False)
        except IOError as e:
            raise Exception("Cannot append dataframe to {}.csv. Exception follows. {}".format(file_name, e))

    if not use_local_storage:
        copy_local_file_to_remote_storage(file_name)

def load_dataframe_from_csv(file_name, use_local_storage):
    """
    Load DataFrame from file csv

    Parameters
    ----------
    file_name (String): Name of file

    Returns
    ----------
    df (DataFrame)
    """    
    df = pd.DataFrame()
    file_path = os.path.join(LOCAL_STORAGE_PATH, file_name) if use_local_storage else os.path.join(REMOTE_STORAGE_PATH, file_name)
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
        except IOError as e:
            raise Exception("Cannot load dataframe from {}.csv. Exception follows. {}".format(file_name, e))

    return df

def copy_local_file_to_remote_storage(file_name):
    """
    Copy csv files from local storage to centralized remote storage
    """
    local_file_path = os.path.join(LOCAL_STORAGE_PATH, file_name)
    remote_file_path = os.path.join(REMOTE_STORAGE_PATH, file_name)

    if os.path.exists(local_file_path):
        try:
            copy(local_file_path, remote_file_path)
        except IOError as e:
            raise IOError("Failed to copy file from local storage: {} to remote storage: {}. Exception follows. {}".format(local_file_path, remote_file_path, e))
        except Exception as e:
            raise Exception("Failed to copy file with exception. {}".format(e))