import logging
import sys
import os

from ..predictor.linear_regression_predictor import LinearRegPredictor
from flask import Blueprint, abort, request, jsonify, Response
from flask_restful import reqparse

predictor_controller = Blueprint('predictor_controller', __name__, template_folder='controller')
LOGGER = logging.getLogger(__name__)

@predictor_controller.route('/predict/<ticker_symbol>', methods=['GET'])
def linear_reg_prediction(ticker_symbol):
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