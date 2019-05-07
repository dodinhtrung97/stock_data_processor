import logging

from ..data_collector.data_collector import DataCollector
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
    parser = reqparse.RequestParser()
    parser.add_argument('daysAhead', type=int, default=1)

    args = parser.parse_args()
    days_ahead = args['daysAhead']

    collector = DataCollector(ticker_symbol=ticker_symbol, period=5)
    collector.run()
    predictor = LinearRegPredictor(collector.results, days_ahead)
    predictor.run()

    response = jsonify({"resultSet": predictor.results}), 200

    return response

