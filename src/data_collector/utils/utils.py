import configparser
import json
import os

def get_collector_config():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, '..', 'conf', 'config.ini')
    config.read(path)

    return config

def get_ticker_list():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, '..', 'conf', 'ticker_list.json')
    
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except IOError as e:
        raise Exception("Cannot load tickers from {}.json. Exception follows. {}".format(file_name, e))
        