from flask import Flask
import logging, threading
from .web_scrapper.utils.utils import *
from .web_scrapper.websocket.ws_server import WSHandler, WSServer

# Setup logging config
setup_logging_with_config('logging.yaml')
SERVER_CONFIG = get_server_config()
LOGGER = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    from src.pattern_matcher.controller.pattern_matcher_controller import pattern_matcher_controller
    app.register_blueprint(pattern_matcher_controller, url_prefix='/api/v0/matcher')
    from src.web_scrapper.controller.scrapper_controller import scrapper_controller
    app.register_blueprint(scrapper_controller, url_prefix='/api/v0/scraper')
    from src.price_predictor.controller.predictor_controller import predictor_controller
    app.register_blueprint(predictor_controller, url_prefix='/api/v0/predictor')

    return app


def create_ws():
    return WSServer([('/news', WSHandler)])