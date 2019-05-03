from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
import logging

LOGGER = logging.getLogger(__name__)

def extract_headline(headline):
	blob = TextBlob(headline)
	print(headline)
	for word, pos in blob.tags:
		word_2 = WordNetLemmatizer().lemmatize(word, 'v')
		print('------', word_2, '|', pos)

extract_headline("IBM acquires Red Hat for US$34 billion")
extract_headline("IBM to acquire Red Hat for US$34 billion")
extract_headline("IBM is acquiring Red Hat for US$34 billion")
extract_headline("IBM is to be acquired by Red Hat for US$34 billion")
extract_headline("IBM to be acquired by Red Hat for US$34 billion")
extract_headline("IBM is acquired by Red Hat for US$34 billion")
extract_headline("IBM acquired by Red Hat for US$34 billion, analyst says")