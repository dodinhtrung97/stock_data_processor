import logging
import sys
import os

from ..processor.data_loader import DataLoader
from ..runner.runner import Runner
from flask import Blueprint, abort, request, jsonify, Response
from flask_restful import reqparse

processor_controller = Blueprint('processor_controller', __name__, template_folder='controller')
LOGGER = logging.getLogger(__name__)

@processor_controller.route('/collect', methods=['GET'])
def collect_data():
    """
    Prase optional arguments in request url if exist
    Only for testing
    """
    params = request.args.to_dict()
    num_threads = int(params['numThreads'])
    use_local_storage = bool(int(params['localStorage']))

    collector_runner = Runner(num_threads, use_local_storage)
    collector_runner.run()

    return jsonify({"status": "Collect successfully!"}), 200

@processor_controller.route('/load/<ticker_symbol>', methods=['GET'])
def load_data(ticker_symbol):
    """
    Prase optional arguments in request url if exist
    Only for testing
    """
    result_set = DataLoader(ticker_symbol).load_json_data()

    if result_set:
        return jsonify({'ticker': ticker_symbol,
                        'resultSet': result_set}), 200
    return jsonify({"error": "Bad Request"}), 400


