import logging
import sys
import os

sys.path.append("..")
from data_collector.collector.data_collector import DataCollector
from ..predictor.linear_regression_predictor import LinearRegPredictor
from flask import Blueprint, abort, request, jsonify, Response
from flask_restful import reqparse

predictor_controller = Blueprint('predictor_controller', __name__, template_folder='controller')
LOGGER = logging.getLogger(__name__)

@predictor_controller.route('/predict/<ticker_symbol>', methods=['POST'])
def predict_url(ticker_symbol):
    """
    Prase optional arguments in request url if exist
    """
    LOGGER.info("Predicting for ticker {}".format(ticker_symbol.upper()))

    params = request.args.to_dict()
    days_ahead = int(params['daysAhead'])
    
    predictor = LinearRegPredictor(DataCollector.load_data_for_ticker(ticker_symbol), days_ahead)
    predictor.run()

    response = jsonify({"resultSet": predictor.results}), 200

    return response
