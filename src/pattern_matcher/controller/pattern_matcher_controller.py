import json
import logging
import os

from ..runner.spearman_runner import SpearManRunner
from ..runner.pearson_runner import PearsonRunner
from ..utils.config_setting import *
from flask import Blueprint, request

logger = logging.getLogger(__name__)
pattern_matcher_controller = Blueprint('pattern_matcher_controller', __name__, template_folder='controller')

def runner_init(): 
    # Initialize a runner
    logger.info('Initializing application ...')
    # read conf
    conf = getconf(logger)
    # init runner
    meaure_type = conf['measurement']['type'].lower()
    global runner
    if meaure_type == 'spearman':
        return SpearManRunner(conf)
    elif meaure_type == 'pearson':
        return PearsonRunner(conf)
    else:
        raise Exception('Unsupported measurement type: {}'.format(meaure_type))

runner = runner_init()
@pattern_matcher_controller.route('/match/', methods=['GET'])
def match():
    params = request.args.to_dict()
    logger.info('Find match pattern with params: %s', params)
    ticker = params['ticker']
    days_back = int(params['days_back'])
    days_forward = int(params['days_forward'])
    top = int(params['top'])
    return json.dumps(runner.run(ticker, days_back, days_forward, top))