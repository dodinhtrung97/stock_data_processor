import configparser, os
import logging.config
import yaml
import json

def setup_logging():
	path = os.path.join('conf', 'logging.yaml')
	env_key = os.getenv('LOG_CFG', None)
	if env_key:
		path = env_key
	if os.path.exists(path):
		with open(path, 'rt') as f:
			config = yaml.safe_load(f.read())
		logging.config.dictConfig(config)
	else:
		logging.basicConfig(level=default_level)

def get_scrapper_config():
	config = configparser.ConfigParser()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	path = os.path.join(dir_path, '..', 'conf', 'config.ini')
	config.read(path)

	return config

def get_verb_dict(logger):
	dir_path = os.path.dirname(os.path.realpath(__file__))
	verb_dict = os.path.join(dir_path, '..', 'conf', 'verb_dict.json')
	try:
		with open(verb_dict, 'r') as f: return json.load(f)
	except IOError as e:
		logger.error('Failed to read json file. Exception follows. %s', e)
		raise Exception('Failed to read json file. Exception follows. {}'.format(e))