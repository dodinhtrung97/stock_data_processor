
class Measurement:
    
    def __init__(self, method):
        self.method = method

    def measure(self, s1, s2):
        return self.method.measure(s1, s2)