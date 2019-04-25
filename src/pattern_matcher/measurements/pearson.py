import logging
import numpy as np

class Pearson:

    def __init__(self, logger = None):
        self.logger = logger or logging.getLogger(__name__)

    def measure(self, s1, s2):
        if len(s1) != len(s2):
            self.logger.info('Invalid input')
        return np.corrcoef(s1, s2, rowvar=False)

if __name__ == "__main__":
    co = PearsonProductMoment()
    x = np.array([[1.1], [1.7], [2.1], [1.4], [0.2]])
    y = np.array([[3.0], [4.2], [4.9], [4.1], [2.5]])
    print(x.shape)
    a = co.measure(x, y)
    print(a)
