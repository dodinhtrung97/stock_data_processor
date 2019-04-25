from textblob import TextBlob
from utils.ticker_symbol import *
import logging

LOGGER = logging.getLogger(__name__)

def score_headline(headline):
	"""
	Determine subjectivity and polarity scores of a statement
	Subjectivity [0, 1] where 0 is objective and 1 is subjective
	Polarity [-1, 1] where -1 is negative and 1 is positive
	"""
	blob = TextBlob(headline)
	(polarity_score, subjectivity_score) = blob.sentiment

	return polarity_score

def is_direct_headline(headline, company_name):
	"""
	Naive extracttion of noun phrases from headline
	Takes first letter of company_name
	"""
	shortened_company_name = company_name.split(' ')[0].lower()
	return shortened_company_name in headline.lower()

def subjectivity_score_to_text(score):
	"""
	Naive conversion of subjectivity score to text
	"""
	if score > 0.8: return "Very Subjective"
	elif score > 0.5: return "Subjective"
	elif score > 0.2: return "Objective"
	else: return "Very Objective"

def polarity_score_to_text(score):
	"""
	Naive conversion of polarity score to text
	"""
	if score < 0.0: return "Negative"
	elif score == 0.0: return "Neutral"
	else: return "Positive"
