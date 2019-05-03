from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer

import logging

from ..utils.ticker_symbol import *
from ..utils.config_setting import get_verb_dict

class headlineAnalyzer():

	LOGGER = logging.getLogger(__name__)

	def __init__(self, headline, company_name, require_sentiment):
		self.__headline = headline.lower()
		self.__company_name = company_name
		self.__require_sentiment = require_sentiment

		self.__verb_dict = get_verb_dict(self.LOGGER)
		self.__verb = ''
		self.__verb_predecessor = ''
		self.__verb_successor = ''
		self.__is_noun_on_verb_rhs = True
		self.__is_passive_voice = False

	def analyze(self):
		score = self.score_headline_naive()

		# Setup evironment for headline analysis
		self.find_effective_verb()

		if self.__verb != '' and self.__verb[0] in self.__verb_dict:
			verb = self.__verb[0]
			potential_score = self.__verb_dict[verb]['value']

			# Verb is effective on company name if company name is on its right hand side
			is_effective_direction_on_verb_rhs = True if self.__verb_dict[verb]['direction'] == 'right' else False
			# Noun on on verb's effective direction
			# Flip noun's position if phrase's voicing is passive
			is_noun_on_verb_effective_direction = self.__is_noun_on_verb_rhs if not self.__is_passive_voice else not self.__is_noun_on_verb_rhs

			if is_noun_on_verb_effective_direction == is_effective_direction_on_verb_rhs:
				score = potential_score

		return (score, self.is_direct_headline()) if self.__require_sentiment else (None, self.is_direct_headline())

	def score_headline_naive(self):
		"""
		Determine subjectivity and polarity scores of a statement
		Subjectivity [0, 1] where 0 is objective and 1 is subjective
		Polarity [-1, 1] where -1 is negative and 1 is positive
		"""
		blob = TextBlob(self.__headline)
		(polarity_score, subjectivity_score) = blob.sentiment

		return self.polarity_score_to_text(polarity_score)

	def is_direct_headline(self):
		"""
		Naive extracttion of noun phrases from headline
		Takes first letter of company_name
		"""
		shortened_company_name = self.__company_name.split(' ')[0].lower()
		return shortened_company_name in self.__headline.lower()

	def find_effective_verb(self):
		"""
		Find verb relative to company name in headline
		Assumes that headline is direct
		Where words of interest are (relative to company name)
		('to', TO) - (rhs)
		('be', VB) - (lhs, rhs)
		('by', IN) - (lhs)
		(<some_verb>, VB) - (rhs)
		"""
		shortened_company_name = self.__company_name.split(' ')[0].lower()
		disected_headline = self.disect_headline()

		# Find company name's index in headline
		company_name_index = 0
		while company_name_index < len(disected_headline):
			if disected_headline[company_name_index][0] != shortened_company_name:
				company_name_index += 1
			else: break

		# Loop right if company name is at the beginning of the sentence
		# Or company name is not precceeded by the word 'by'
		# Else loop left
		# Look for a verb that is not 'be'
		if company_name_index != 0 or disected_headline[company_name_index - 1][1] == 'IN': self.find_verb_on_lhs(disected_headline, company_name_index)
		else: self.find_verb_on_rhs(disected_headline, company_name_index)

		# Determine if effective phrase is passive
		self.is_passive_voice()

	def find_verb_on_rhs(self, disected_headline, company_name_index):
		"""
		Find verb on the right hand side of company name
		"""
		self.__is_noun_on_verb_rhs = False
		word_index = company_name_index + 1

		while word_index < len(disected_headline):
			word, tag = disected_headline[word_index]

			if ('VB' in tag) and (word != 'be'):
				pred_word_with_tag = disected_headline[word_index - 1]
				succ_word_with_tag = disected_headline[word_index + 1]

				self.__verb = (word, tag)
				self.__verb_predecessor = pred_word_with_tag
				self.__verb_successor = succ_word_with_tag
				break
			else:
				word_index += 1

	def find_verb_on_lhs(self, disected_headline, company_name_index):
		"""
		Find verb on the left hand side of company name
		"""
		self.__is_noun_on_verb_rhs = True
		word_index = company_name_index - 1

		while word_index > 0:
			word, tag = disected_headline[word_index]

			if ('VB' in tag) and (word != 'be'):
				pred_word_with_tag = disected_headline[word_index - 1]
				succ_word_with_tag = disected_headline[word_index + 1]

				self.__verb = (word, tag)
				self.__verb_predecessor = pred_word_with_tag
				self.__verb_successor = succ_word_with_tag
				break
			else:
				word_index -= 1

	def is_passive_voice(self):
		"""
		Determine if a phrase is passively voiced
		If 'by' succeeds or <to_be> preceeds <verb> then phrase is passive
		Eg: A is acquired by B
		"""
		if self.__verb_successor != '' and self.__verb_predecessor != '':
			self.__is_passive_voice = (self.__verb_successor[1] == 'IN' or self.__verb_predecessor[1] == 'VB')
		else:
			self.__is_passive_voice = False

	def disect_headline(self):
		"""
		Disect a headline string into a list of tagged words
		"""
		disected_headline = []

		blob = TextBlob(self.__headline)
		for word, pos in blob.tags:
			word_2 = WordNetLemmatizer().lemmatize(word, 'v')
			disected_headline.append((word_2, pos))

		return disected_headline

	def polarity_score_to_text(self, score):
		"""
		Naive conversion of polarity score to text
		"""
		if score < 0.0: return "-"
		elif score == 0.0: return "0"
		else: return "+"