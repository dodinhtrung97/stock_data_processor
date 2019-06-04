from ..measurements.spearmanr import Spearmanr
from ..measurements.pearson import Pearson
from ..measurements.measurement import Measurement
from ..loader import csv_loader as loader

import sys, logging
import numpy as np
import time

class Matcher:

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def match(self, base, ticker, dataframe, pattern, days_forward=30, steps=1):
        pass

class SpearmanMatcher(Matcher):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        Matcher.__init__(self)
        self.__measurement = Measurement(Spearmanr())

    def match(self, base, ticker, dataframe, pattern, days_forward=30, steps=1):
        start = time.time() - base

        window_size = len(pattern)
        max = sys.float_info.min
        i, fr, to = 0, None, None
        
        while (i + window_size) < dataframe.shape[0] - days_forward:
            batch = dataframe.iloc[i:i+window_size, 1].values
            # calculate the measurement
            value = self.__measurement.measure(pattern, batch)
            if value[0] > max:
                max = value[0]
                fr, to = i, i + window_size
            # window increment
            i = i + steps
        # return max value and data from dataframe accordingly
        match_close_result = dataframe.iloc[fr:to, 1].to_list()
        match_date_result = dataframe.iloc[fr:to, 0].to_list()
        predict_close_result = dataframe.iloc[to:to + days_forward, 1].to_list()
        predict_date_result = dataframe.iloc[to:to + days_forward, 0].to_list()
        
        stop = time.time() - base
        return ticker, max, (match_close_result, match_date_result, predict_close_result, predict_date_result), (start, stop), dataframe.shape[0]

class PearsonMatcher(Matcher):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        Matcher.__init__(self)
        self.__measurement = Measurement(Pearson())
    
    def match(self, base, ticker, dataframe, pattern, days_forward=30, steps=1):
        start = time.time() - base

        window_size = len(pattern)
        max = sys.float_info.min
        i, fr, to = 0, None, None
        
        while (i + window_size) < dataframe.shape[0] - days_forward:
            batch = dataframe.iloc[i:i+window_size, 1].values
            # calculate the measurement
            value = self.__measurement.measure(pattern, batch)
            if value[0][1] > max:
                max = value[0][1]
                fr, to = i, i + window_size
            # window increment
            i = i + steps
        # return max value and data from dataframe accordingly
        match_close_result = dataframe.iloc[fr:to, 1].to_list()
        match_date_result = dataframe.iloc[fr:to, 0].to_list()
        predict_close_result = dataframe.iloc[to:to + days_forward, 1].to_list()
        predict_date_result = dataframe.iloc[to:to + days_forward, 0].to_list()
        
        stop = time.time() - base
        return ticker, max, (match_close_result, match_date_result, predict_close_result, predict_date_result), (start, stop), dataframe.shape[0]


