from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
from collections import namedtuple

import logging

from ..utils.ticker_symbol import *
from ..utils.utils import get_verb_dict
from ..utils.utils import reversed_enumerate

class headlineAnalyzer():

    LOGGER = logging.getLogger(__name__)

    def __init__(self, headline, company_name):
        self.__headline = headline.lower()
        self.__company_name = company_name

        self.__disected_headline = self.disect_headline()
        self.__known_verb_dict = get_verb_dict(self.LOGGER)
        self.__verb = tuple()
        self.__verb_predecessor = tuple()
        self.__verb_successor = tuple()
        self.__is_noun_on_verb_rhs = None
        self.__is_passive_voice = None

    def analyze(self):
        """
        Attempt to enrich scoring by using custom scoring algorithm
        Failing that, use textblob's sentiment analysis for scoring
        """
        score = self.score_headline_naive()
        company_name_index_list = self.find_company_name_in_headline()

        for company_name_index in company_name_index_list:

            # Setup evironment for analysis
            self.find_effective_verb(company_name_index)
            # Determine if effective phrase is passive
            self.determine_voicing_passitivity()

            if self.__verb and self.__verb.word in self.__known_verb_dict:
                verb = self.__verb.word
                potential_score = self.__known_verb_dict[verb]['value']

                # Verb is effective on company name if company name is on its right hand side
                is_effective_direction_on_verb_rhs = True if self.__known_verb_dict[verb]['direction'] == 'right' else False
                # Noun's on verb right hand side in active sentence voicing
                # Eg: Apple is acquired by Amazon -> Amazon acquired Apple -> Apple's active direction on rhs
                # Flip noun's position if phrase's voicing is passive
                is_noun_active_direction_on_rhs = self.__is_noun_on_verb_rhs if not self.__is_passive_voice else not self.__is_noun_on_verb_rhs

                if is_noun_active_direction_on_rhs == is_effective_direction_on_verb_rhs:
                    score = potential_score
                    break

        analysis_result = namedtuple("AnalysisResult", ['score', 'direct'])
        return analysis_result(score=score, direct=self.is_direct_headline())

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

    def find_effective_verb(self, company_name_index):
        """
        Find verb relative to company name in headline
        Assumes that headline is direct
        Where words of interest are (relative to company name)
        ('to', TO) - (rhs)
        ('be', VB) - (lhs, rhs)
        ('by', IN) - (lhs)
        (<some_verb>, VB) - (rhs)

        Loop right if company name is at the beginning of the sentence
        Or company name is not precceeded by the word 'by'
        Else loop left
        Look for a verb that is not 'be'
        """

        # Reset variables
        self.__verb = tuple()
        self.__verb_predecessor = tuple()
        self.__verb_successor = tuple()

        disected_headline = self.__disected_headline

        if company_name_index == 0 or (disected_headline[company_name_index-1].tag != 'IN' and 'VB' not in disected_headline[company_name_index-1].tag):
            self.find_verb_on_rhs(company_name_index)
        else: self.find_verb_on_lhs(company_name_index)

    def find_company_name_in_headline(self):
        """
        Find company name's indexes in headline
        """
        shortened_company_name = self.__company_name.split(' ')[0].lower()
        disected_headline = self.__disected_headline
        result = []

        company_name_index = 0
        for company_name_index, company_name in enumerate(disected_headline):
            if disected_headline[company_name_index].word == shortened_company_name: 
                result.append(company_name_index)

        return result

    def find_verb_on_rhs(self, company_name_index):
        """
        Find verb on the right hand side of company name
        """
        disected_headline = self.__disected_headline
        self.__is_noun_on_verb_rhs = False

        for word_index, word in enumerate(disected_headline[company_name_index:], start=company_name_index):
            word, tag = word
            word_tuple = namedtuple("Word", ['word', 'tag'])

            if ('VB' in tag) and (word != 'be'):
                pred_word = disected_headline[word_index - 1]
                succ_word = disected_headline[word_index + 1]

                self.__verb = word_tuple(word=word, tag=tag)
                self.__verb_predecessor = word_tuple(word=pred_word.word, tag=pred_word.tag)
                self.__verb_successor = word_tuple(word=succ_word.word, tag=succ_word.tag)
                break

    def find_verb_on_lhs(self, company_name_index):
        """
        Find verb on the left hand side of company name
        """
        disected_headline = self.__disected_headline
        self.__is_noun_on_verb_rhs = True

        for word_index, word in reversed_enumerate(disected_headline[:company_name_index], start=company_name_index):
            word, tag = word
            word_tuple = namedtuple("Word", ['word', 'tag'])

            if ('VB' in tag) and (word != 'be'):
                pred_word = disected_headline[word_index - 1]
                succ_word = disected_headline[word_index + 1]

                self.__verb = word_tuple(word=word, tag=tag)
                self.__verb_predecessor = word_tuple(word=pred_word.word, tag=pred_word.tag)
                self.__verb_successor = word_tuple(word=succ_word.word, tag=succ_word.tag)
                break

    def determine_voicing_passitivity(self):
        """
        Determine if a phrase is passively voiced
        If 'by' succeeds or <to_be> preceeds <verb> then phrase is passive
        Unless <to_be> preceeds a <verb> that is in -ing form
        Eg: A is acquired by B
        """
        if self.__verb_successor and self.__verb_predecessor:
            self.__is_passive_voice = (('VB' in self.__verb_predecessor.tag and self.__verb.tag != 'VBG') or self.__verb_successor.word == 'by')
        else:
            self.__is_passive_voice = False

    def disect_headline(self):
        """
        Disect a headline string into a list of tagged words
        """
        disected_headline = []

        blob = TextBlob(self.__headline)
        for word, tag in blob.tags:
            word_tuple = namedtuple('Word', ['word', 'tag'])
            word_2 = WordNetLemmatizer().lemmatize(word, 'v')
            # Some words can be both noun AND verd (eg: misses)
            # If a word can be lemmatized into its base form, assume it is VB (Verb in base form)
            # Unless said word is already a verb (eg: VBG)
            # Eg: misses -> miss
            disected_headline.append(word_tuple(word=word_2, tag='VB')) if 'VB' not in tag and word_2 != word else disected_headline.append(word_tuple(word=word_2, tag=tag))

        return disected_headline

    def polarity_score_to_text(self, score):
        """
        Naive conversion of polarity score to text
        """
        if score < 0.0: return "-"
        elif score == 0.0: return "0"
        else: return "+"