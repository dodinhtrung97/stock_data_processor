import json, os, yaml
import logging.config

def parse_json_file(conf_file, logger):
    try:
        with open(conf_file, 'r') as f:
            logger.info('Retrieving pattern matcher config from: %s', conf_file)
            return json.load(f)
    except IOError as e:
        logger.error('Failed to read json file. Exception follows. %s', e)
        raise Exception('Failed to read json file. Exception follows. {}'.format(e))
    
def getconf(conf_file, logger):
    conf = parse_json_file(conf_file, logger)
    logger.info('Pattern matcher running with the following configs: %s', str(conf))
    return conf