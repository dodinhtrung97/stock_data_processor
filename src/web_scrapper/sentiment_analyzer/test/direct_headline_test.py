from textblob import TextBlob
import time
import logging

def is_direct_headline_test(sentence, ticker_symbol, company_name):
	"""
	Extraction of noun phrases from sentence
	Find all nouns in input sentence and check those against company_name

	Args:
	    sentence (String): sentence
	
	Returns:
	    List[]: List of nouns 
	"""
	blob = TextBlob(sentence)
	noun_phrases = blob.noun_phrases
	
	for noun in noun_phrases:
		if noun in company_name.lower():
			return True

	return False

def is_direct_headline_naive_test(sentence, ticker_symbol, company_name):
	"""
	Naive extraction of noun phrases from sentence
	Takes first letter of company name retrieved from get_company_name_by_symbol
	
	Args:
	    sentence (TYPE): Description
	    ticker_symbol (TYPE): Description
	
	Returns:
	    TYPE: Description
	"""
	shortened_company_name = company_name.split(' ')[0].lower()

	return shortened_company_name in sentence.lower()

def execution_time_per_headline_test(result_set, ticker_symbol="AAPL", company_name="Apple Inc."):
	"""
	Test is_direct_headline_test's execution time against is_direct_headline_naive_test
	
	Args:
	    sentence (TYPE): Description
	    ticker_symbol (TYPE): Description
	"""
	execution_time_dict = {}

	for result in result_set['ResultSet']: 
		time_start = time.time()
		is_direct_headline_test(result['headline'], ticker_symbol, company_name)
		time_end = time.time()

		time_start_naive = time.time()
		is_direct_headline_naive_test(result['headline'], ticker_symbol, company_name)
		time_end_naive = time.time()

		execution_time_dict[result['headline']] = ((time_end - time_start), (time_end_naive - time_start_naive))

	# Print results
	key_list = execution_time_dict.keys()
	print('%-130s%-40s%-40s' % ("NEWS_HEADLINE", "ML_EXECUTION_TIME(s)", "NAIVE_EXECUTION_TIME(s)"))
	for key in key_list:
		(ml_execution_time, naive_execution_time) = execution_time_dict[key]
		print('%-130s%-40f%-40f' % (key, ml_execution_time, naive_execution_time))

def execution_time_total_test(result_set, ticker_symbol="AAPL", company_name="Apple Inc."):
	"""
	Test is_direct_headline_test's execution time against is_direct_headline_naive_test
	
	Args:
	    sentence (TYPE): Description
	    ticker_symbol (TYPE): Description
	"""
	execution_time_dict = {}

	time_start = time.time()
	for result in result_set['ResultSet']:
		is_direct_headline_test(result['headline'], ticker_symbol, company_name)
	time_end = time.time()
	ml_execution_time = time_end - time_start

	time_start = time.time()
	for result in result_set['ResultSet']:
		is_direct_headline_naive_test(result['headline'], ticker_symbol, company_name)
	time_end = time.time()
	naive_execution_time = time_end - time_start

	# Print results
	print('%-130s%-40s%-40s' % ("TOTAL_HEADLINES", "ML_EXECUTION_TIME(s)", "NAIVE_EXECUTION_TIME(s)"))
	print('%-130s%-40f%-40f' % (len(result_set['ResultSet']), ml_execution_time, naive_execution_time))


result_set = {
						    "ResultSet": [
						        {
						            "date": "4hrs ago - CNBC.com",
						            "directHeadline": False,
						            "headline": "Stocks in Asia inch up as investors watch US-China trade developments",
						            "polarity": "Neutral",
						            "subjectivity": "Very Objective"
						        },
						        {
						            "date": "6hrs ago - CNBC.com",
						            "directHeadline": True,
						            "headline": "Cramer: Delta, Apple, and Home Depot are buys as investors worry about rising labor, oil costs",
						            "polarity": "Neutral",
						            "subjectivity": "Very Objective"
						        },
						        {
						            "date": "8hrs ago - CNBC.com",
						            "directHeadline": False,
						            "headline": "CBS missed its internal deadline to name a new CEO — and don't expect a decision soon",
						            "polarity": "Positive",
						            "subjectivity": "Very Objective"
						        },
						        {
						            "date": "10hrs ago - CNBC.com",
						            "directHeadline": True,
						            "headline": "Apple has another new set of wireless headphones for people who don't want AirPods",
						            "polarity": "Positive",
						            "subjectivity": "Very Objective"
						        },
						        {
						            "date": "11hrs ago - CNBC.com",
						            "directHeadline": False,
						            "headline": "Top Silicon Valley investor: This is what gives Elon Musk 'True superpowers' in business",
						            "polarity": "Positive",
						            "subjectivity": "Objective"
						        },
						        {
						            "date": "12hrs ago - CNBC.com",
						            "directHeadline": False,
						            "headline": "This iPhone trick makes Face ID faster and lets you wear sunglasses when you're unlocking your phone",
						            "polarity": "Neutral",
						            "subjectivity": "Very Objective"
						        },
						        {
						            "date": "13hrs ago - CNBC.com",
						            "directHeadline": True,
						            "headline": "Apple's first new subscription service is unlikely to move the needle toward the company's lofty goals for services",
						            "polarity": "Positive",
						            "subjectivity": "Very Objective"
						        },
						        {
						            "date": "15hrs ago - CNBC.com",
						            "directHeadline": False,
						            "headline": "Your first trade for Wednesday, April 3",
						            "polarity": "Positive",
						            "subjectivity": "Objective"
						        },
						        {
						            "date": "16hrs ago - CNBC.com",
						            "directHeadline": True,
						            "headline": "Apple won't have a 5G iPhone anytime soon, UBS says",
						            "polarity": "Neutral",
						            "subjectivity": "Very Objective"
						        },
						        {
						            "date": "17hrs ago - CNBC.com",
						            "directHeadline": False,
						            "headline": "Stocks set to rise | Caterpillar shares fall | US-China reportedly near trade deal",
						            "polarity": "Positive",
						            "subjectivity": "Very Objective"
						        }
						    ]}
execution_time_per_headline_test(result_set)