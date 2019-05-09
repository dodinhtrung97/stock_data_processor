import configparser, os

def get_predictor_config():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, '..', 'conf', 'config.ini')
    config.read(path)

    return config