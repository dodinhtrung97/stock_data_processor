import configparser
import os
import yaml
import logging

def getconf(logger):
	config = configparser.ConfigParser()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	path = os.path.join(dir_path, '..', '..', '..', 'conf', 'config.ini')
	config.read(path)

	input = config._sections['INPUT']
	measurement = config._sections['MEASUREMENT']

	conf = {'input': input, 'measurement': measurement}
	logger.info('App running with the following configs: {}'.format(conf))
	return conf