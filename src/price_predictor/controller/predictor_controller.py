import logging
import sys
import os

from data_collector.collector.data_collector import DataCollector
from data_collector.utils.utils import get_ticker_list
from data_collector.runner.runner import Runner
from ..predictor.linear_regression_predictor import LinearRegPredictor
from ..predictor.prophet_predictor import ProphetPredictor
from flask import Blueprint, abort, request, jsonify, Response
from flask_restful import reqparse

predictor_controller = Blueprint('predictor_controller', __name__, template_folder='controller')
LOGGER = logging.getLogger(__name__)

@predictor_controller.route('/predict/<ticker_symbol>', methods=['GET'])
def predict_url(ticker_symbol):
    """
    Prase optional arguments in request url if exist
    """
    LOGGER.info("Predicting for ticker {}".format(ticker_symbol.upper()))

    params = request.args.to_dict()
    days_ahead = int(params['daysAhead'])

    predictor = LinearRegPredictor(ticker_symbol, days_ahead)

    predictor.run()

    response = jsonify({"predictions": predictor.results}), 200

    return response
