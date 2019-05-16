import logging
import sys
import os

sys.path.append("..")
from data_collector.collector.data_collector import DataCollector
from data_collector.utils.utils import get_ticker_list
from data_collector.runner.runner import Runner
from ..predictor.linear_regression_predictor import LinearRegPredictor
from flask import Blueprint, abort, request, jsonify, Response
from flask_restful import reqparse

predictor_controller = Blueprint('predictor_controller', __name__, template_folder='controller')
LOGGER = logging.getLogger(__name__)

@predictor_controller.route('/predict/<ticker_symbol>', methods=['GET'])
def predict_url(ticker_symbol):
    """
    Prase optional arguments in request url if exist
    """
    params = request.args.to_dict()
    days_ahead = int(params['daysAhead'])

    # Test Data Collector with multi-threads
    # No need to run 2 lines below if Data Collector is set independently
    collector_runner = Runner(num_threads=4)
    collector_runner.run()
    
    predictor = LinearRegPredictor(DataCollector.load_data_for_ticker(ticker_symbol), days_ahead)
    predictor.run()

    response = jsonify({"resultSet": predictor.results}), 200

    return response

