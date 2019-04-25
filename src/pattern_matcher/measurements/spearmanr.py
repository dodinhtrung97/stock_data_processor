import logging
import scipy.stats as stats
import numpy as np

# Currently using Pearson correlation coedffecient
class Spearmanr:

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def measure(self, s1, s2):
        if len(s1) != len(s2):
            self.logger.error('Invalid input')
            return
        return stats.spearmanr(s1, s2)
