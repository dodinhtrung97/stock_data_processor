import logging

from scrapper.scrapper import scrapper
from flask import Blueprint, abort, request, jsonify, Response
from flask_restful import reqparse

scrapper_controller = Blueprint('scrapper_controller', __name__, template_folder='controller')
LOGGER = logging.getLogger(__name__)

@scrapper_controller.route('/scrape/<news_source>/<ticker_symbol>', methods=['POST'])
def scrape_url(news_source, ticker_symbol):
	"""
	Prase optional arguments in request url if exist
	"""
	parser = reqparse.RequestParser()
	parser.add_argument('getDate', type=int, default=False)
	parser.add_argument('getSentiment', type=int, default=False)
	parser.add_argument('withinHours', type=int, default=24)

	args = parser.parse_args()
	get_date = bool(args['getDate'])
	get_sentiment = bool(args['getSentiment'])
	within_hours = args['withinHours']

	request_content = request.get_json()
	
	try:
		walking_pattern_xpath = request_content['walkingPattern']
		headline_pattern_xpath = request_content['headlinePattern']
		date_pattern_xpath = request_content['datePattern'] if get_date else None

		web_scrapper = scrapper(news_source=news_source,
								ticker_symbol=ticker_symbol, 
								walking_pattern_xpath=walking_pattern_xpath, 
								headline_pattern_xpath=headline_pattern_xpath,
								within_hours=within_hours, 
								date_pattern_xpath=date_pattern_xpath, 
								require_sentiment=get_sentiment)

		web_scrapper.scrape()
		response = jsonify({"resultSet": web_scrapper.results}), 200
		
		return response
	except Exception as e:
		LOGGER.error("Bad Request with exception: {}".format(e))
		return jsonify({"error": "Bad request"}), 400

@scrapper_controller.route('/get_company_name/<ticker_symbol>', methods=['GET'])
def get_company_name_by_ticker_symbol(ticker_symbol):
	company_name = get_company_name_by_symbol(ticker_symbol)

	if company_name is not None:
		return jsonify({'name': company_name}), 200
	LOGGER.error("Bad Request")
	return jsonify({"error": "Bad Request"}), 400

@scrapper_controller.route('/get_company_suggestion/<ticker_symbol>', methods=['GET'])
def get_company_sugesstion_by_ticker_symbol(ticker_symbol):
	suggestions = get_suggestion_by_symbol(ticker_symbol)

	if suggestions is not None:
		return jsonify({'ResultSet': suggestions}), 200
	LOGGER.error("Bad Request")
	return jsonify({"error": "Bad Request"}), 400