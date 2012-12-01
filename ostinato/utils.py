import time

class benchmark(object):
    """
    A simple benchmarking class borrowed from:
    http://dabeaz.blogspot.co.uk/2010/02/context-manager-for-timing-benchmarks.html
    """
    def __init__(self,name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self,ty,val,tb):
        end = time.time()
        print("%s : %0.3f seconds" % (self.name, end-self.start))
        return False

