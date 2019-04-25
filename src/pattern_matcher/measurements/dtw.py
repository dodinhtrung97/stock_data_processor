from dtw import dtw

class DTW:

    def __init__(self, dist_func):
        self.dist_func = dist_func

    def measure(self, s1, s2):
        return dtw(s1, s2, dist = self.dist_func)