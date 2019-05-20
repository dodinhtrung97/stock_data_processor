import logging
import sys
import os

from ..collector.data_collector import DataCollector
from ..runner.runner import Runner
from flask import Blueprint, abort, request, jsonify, Response
from flask_restful import reqparse

collector_controller = Blueprint('collector_controller', __name__, template_folder='controller')
LOGGER = logging.getLogger(__name__)

@collector_controller.route('/collect', methods=['GET'])
def collect_url():
    """
    Prase optional arguments in request url if exist
    Only for testing
    """
    params = request.args.to_dict()
    num_threads = int(params['numThreads'])

    collector_runner = Runner(num_threads)
    collector_runner.run()

    response = jsonify({"status": "Collect successfully!"}), 200

    return response
