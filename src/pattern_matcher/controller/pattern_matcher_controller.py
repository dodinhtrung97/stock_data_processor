import json
import logging
import os
import threading, schedule, time

from ..runner.spearman_runner import SpearManRunner
from ..runner.pearson_runner import PearsonRunner
from ..conf.app_conf import *
from flask import Blueprint, request

logger = logging.getLogger(__name__)
pattern_matcher_controller = Blueprint('pattern_matcher_controller', __name__, template_folder='controller')
runner = None

def runner_init(): 
    conf_file = os.path.join(os.path.dirname(__file__), '..', 'conf', 'conf.json')
    # Initialize a runner
    logger.info('Initializing application ...')
    # read conf
    conf = getconf(conf_file, logger)
    # init runner
    meaure_type = conf['measurement']['type'].lower()
    global runner
    if meaure_type == 'spearman':
        runner = SpearManRunner(conf)
    elif meaure_type == 'pearson':
        runner = PearsonRunner(conf)
    else:
        raise Exception('Unsupported measurement type: {}'.format(meaure_type))
    # run update runner
    scheduler_thread = threading.Thread(target=update_runner, daemon=True)
    scheduler_thread.start()

def update_runner():
    while True:
        logger.info("Updating new collected data ...")
        schedule.run_pending()
        time.sleep(3600)

runner_init()
schedule.every().day.at("00:05").do(runner_init)
@pattern_matcher_controller.route('/match/', methods=['GET'])
def match():
    params = request.args.to_dict()
    logger.info('Find match pattern with params: %s', params)
    ticker = params['ticker'].upper()
    days_back = int(params['days_back'])
    days_forward = int(params['days_forward'])
    top = int(params['top'])
    return json.dumps(runner.run(ticker, days_back, days_forward, top))