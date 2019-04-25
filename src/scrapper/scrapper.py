import sys
import logging
import time

from bs4 import BeautifulSoup

from .get_requests import get_html_response
from headline_sentiment_analysis.sentiment_analyzer import *
from utils.xpath import Xpath
from utils.date_time import customTime
from utils.ticker_symbol import generate_url, get_company_name_by_symbol
from utils.config_setting import get_config

class scrapper:

	"""Summary
	
	Attributes:
	    date_pattern (Tuple(element_name, Dict(attribute_name, attribute_value))): pattern to retrieve date from html
	    headline_pattern (Tuple(element_name, Dict(attribute_name, attribute_value))): pattern to retrieve headline from html
	    html (html): final html after having gone through find_lowest_children
	    lowest_children (TYPE): Description
	    news_source (TYPE): eg: CNBC, BENZINGA
	    require_sentiment (bool, optional): Description
	    results (TYPE): Description
	    ticker_symbol (TYPE): Stock code
	                          eg: AAPL for Apple Inc.
	    walking_pattern (TYPE): Description
	"""

	LOGGER = logging.getLogger(__name__)
	CONFIG = get_config()
	
	def __init__(self, 
				 news_source,
				 ticker_symbol, 
				 walking_pattern_xpath, 
				 headline_pattern_xpath, 
				 within_hours,
				 date_pattern_xpath=None, 
				 require_sentiment=False):
		self.news_source = news_source.upper()
		self.ticker_symbol = ticker_symbol.upper()
		self.walking_pattern = Xpath(walking_pattern_xpath).to_pattern()
		self.headline_pattern = Xpath(headline_pattern_xpath).to_pattern()
		self.date_pattern = Xpath(date_pattern_xpath).to_pattern() if date_pattern_xpath is not None else None
		self.require_sentiment = require_sentiment
		self.within_hours = within_hours

		self.__company_name = get_company_name_by_symbol(self.ticker_symbol)
		self.__html = ''
		self.__lowest_children = None
		self.results = None

		# Load extra data into object
		self.is_known_news_source()

	def scrape(self):
		"""
		Start scrapping
		
		Returns:
		    list(Dict(headline: date)): list of (headline: date) scrapped from given news site (check utils/url_generation.py)
		"""
		self.scrape_with_ticker_symbol()
		if self.__lowest_children is not None:
			results = self.find_headline_info_with_pattern()
			parsed_results = []
			for headline in results:
				parsed_results.append({key: value for key, value in headline.items() if value is not None})

			self.results = parsed_results

	def find_headline_info_with_pattern(self):
		"""
		Finds url, headline and date info from html given headline pattern and date pattern
		Assumes url is href'd in headline

		Returns:
		    headline_date_dict (see below): list of Dict{} scrapped from given news site (check utils/url_generation.py)
		    Optional Dict keys includes: directHeadline, subjectivity, polarity
		"""
		headline_list = []

		for child in self.__lowest_children:
			# Assume hyperlink is on headline
			url = self.find_extra_element_by_condition(child, self.headline_pattern).get('href')
			headline = self.find_extra_element_by_condition(child, self.headline_pattern)
			headline = headline.text.strip()

			publish_date = self.find_extra_element_by_condition(child, self.date_pattern) if self.date_pattern is not None else None
			publish_date = publish_date.text.strip()

			direct_headline = is_direct_headline(headline, self.__company_name)
			polarity_score = score_headline(headline) if self.require_sentiment else (None, None)

			# Format date
			publish_date_epoch = customTime(news_source=self.news_source, arbitrary_time=publish_date).to_epoch_time() if publish_date is not None else None

			# Ignore headlines outside of desired hour frame
			if not self.is_within_hours(publish_date_epoch):
				continue

			headline_date_dict = {'url': url,
								  'headline': headline,
								  'date': publish_date_epoch,
								  'direct': direct_headline,
								  'score': polarity_score}

			headline_list.append(headline_date_dict)

		return headline_list

	def scrape_with_ticker_symbol(self):
		"""
		Scrapes an html response by walking down walking_pattern
		Failing that, returns an error message

		Returns:
		    TYPE: list of last element(s) html in walking_pattern
		"""
		url = generate_url(self.news_source, self.ticker_symbol)
		response = get_html_response(url)

		if response is not None:
			html = BeautifulSoup(response, 'html.parser')

			self.__html = html
			return self.find_lowest_children(self.__html, self.walking_pattern)
		else:
			self.LOGGER.error("Connection to designated url failed")

	def find_lowest_children(self, reduced_html, walking_pattern):
		"""
		Child process of scrape_with_ticker_symbol
		Find lowest child in an reduced_html tree in the form of a list of path from a parent node to a next child
		
		Args:
		    reduced_html (reduced_html): Reduced reduced_html
		    walking_pattern (list(element_name, Dict(attribute_name: attrivute_value), index)): walking pattern from top parent to lowest child
		
		Returns:
		    reduced_html: reduced_html of lowest child in walking_pattern
		"""
		if len(walking_pattern) == 0:
			self.__lowest_children = reduced_html
			return reduced_html
		else:
			child_element_name = walking_pattern[0][0]
			child_element_attrs = walking_pattern[0][1]

			try:
				pivot_list = reduced_html.find_all(child_element_name, attrs=child_element_attrs)
				# Recursively walks down each tree level
				if len(walking_pattern[0]) == 3:
					child_element_index = walking_pattern[0][2]
					return self.find_lowest_children(pivot_list[child_element_index], walking_pattern[1:])
				else:
					return self.find_lowest_children(pivot_list, walking_pattern[1:])
			except IndexError as e:
				self.LOGGER.error(f"Failed to scrape where child_element_name: {child_element_name} and child_element_attrs: {child_element_attrs} with exception {e}")
				return
			except AttributeError as e:
				self.LOGGER.error(f"Failed to walk further at {child_element_name} and {child_element_attrs} with exception {e}")
				return

	def find_extra_element_by_condition(self, reduced_html, pattern):
		"""
		Find extra element eg: headline, date
		If pattern includes an index then find element at given index
		Else find normally
		
		Args:
			reduced_html: Current reduced html to walk from
		    pattern (TYPE): Description
		
		Returns:
		    TYPE: Description
		
		Raises:
		    SyntaxError: Pattern length is not 2 or 3
		"""
		if len(pattern) == 2:
			element = reduced_html.find(pattern[0], attrs=pattern[1])
		elif len(pattern) == 3:
			element = reduced_html.findAll(pattern[0], attrs=pattern[1])[pattern[2]]
		else:
			raise SyntaxError("Wrong headline pattern input: {}".format(pattern))
		return element

	def is_within_hours(self, publish_time):
		"""
		Check if time since article publish is within desired time range
		
		Args:
		    publish_time (TYPE): News publish time
		
		Returns:
		    TYPE: Description
		"""
		current_time = time.time()
		return float(self.within_hours) >= (current_time - publish_time)/3600

	def is_known_news_source(self):
		"""
		Check if init news source is known
		
		Raises:
		    ValueError: Unknown news source
		"""
		news_source_list = dict(self.CONFIG['NEWS_SOURCE']).keys()
		if not self.news_source.lower() in news_source_list:
			raise ValueError("Unknown new source, list of known news source includes {}".format(list(news_source_list)))