import requests
import configparser
import os
import logging

from utils.config_setting import get_config

CONFIG = get_config()
LOGGER = logging.getLogger(__name__)

def generate_url(news_source, ticker_symbol):
	"""
	Returns self-generated CNBC url for given ticker_symbol
	Url is news tab
	"""
	return CONFIG['NEWS_SOURCE'][news_source].format(ticker_symbol)

def get_company_name_by_symbol(symbol):
    """
	Get company name by symbol using established API
    """
    url = CONFIG['EXTERNAL_API']['TICKER_SYMBOL_API'].format(symbol)

    result = requests.get(url).json()
    company_name = ''

    for company in result['ResultSet']['Result']:
        if company['symbol'] == symbol:
            company_name = company['name']

    if company_name != None:
        return company_name
    else:
        raise AttributeError("Failed to find company with input ticker symbol: {}".format(symbol))

def get_suggestion_by_symbol(symbol):
    """
	Get suggestion for company's ticker symbol and name by input ticker symbol
    """
    url = CONFIG['EXTERNAL_API']['TICKER_SYMBOL_API'].format(symbol)

    result = requests.get(url).json()

    symbol_to_company_list = []

    for company in result['ResultSet']['Result']:
        symbol_to_company_list.append({
        		'symbol': company['symbol'],
        		'name': company['name']
        	})

    return symbol_to_company_list