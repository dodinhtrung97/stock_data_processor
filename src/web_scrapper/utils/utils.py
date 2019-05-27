import configparser, os
import logging.config
import yaml
import json
import itertools

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

def setup_server_logging(default_level='DEBUG'):
    """
    Set server logging config
    See: conf/logging.yaml
    """
    path = os.path.join(DIR_PATH, '..', '..', '..', 'conf', 'logging.yaml')
    env_key = os.getenv('LOG_CFG', None)

    if env_key: path = env_key

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def setup_service_logging(log_dir_path, default_level='DEBUG'):
    """
    Set windows service logging config
    See: conf/windows_service_logging.yaml
    """
    path = os.path.join(DIR_PATH, '..', '..', '..', 'conf', 'windows_service_logging.yaml')
    env_key = os.getenv('SERVICE_LOG_CFG', None)

    if env_key: path = env_key

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
            config['handlers']['info_file_handler']['filename'] = config['handlers']['info_file_handler']['filename'].format(log_dir_path = log_dir_path)
            config['handlers']['error_file_handler']['filename'] = config['handlers']['error_file_handler']['filename'].format(log_dir_path = log_dir_path)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def get_scrapper_config():
    config = configparser.ConfigParser()
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(DIR_PATH, '..', 'conf', 'config.ini')
    config.read(path)

    return config

def get_server_config():
    config = configparser.ConfigParser()
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(DIR_PATH, '..', '..', '..', 'conf', 'config.ini')
    config.read(path)

    return config

def get_verb_dict(logger):
    file_name = 'verb_dict.json'
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    verb_dict = os.path.join(DIR_PATH, '..', 'conf', 'verb_dict.json')
    try:
        with open(verb_dict, 'r') as f: return json.load(f)
    except IOError as e:
        logger.error('Failed to read file {}. Exception follows. {}'.format(file_name, e))
        raise Exception('Failed to read file {}. Exception follows. {}'.format(file_name, e))

def reversed_enumerate(sequence, start):
    sequence = sequence[:start]
    return zip(
        reversed(range(len(sequence))),
        reversed(sequence),
    )