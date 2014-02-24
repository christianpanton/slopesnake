

"""
    Cache previously calculated energies
"""

class Cache(object):

    def __init__(self, callback):
        self.callback = callback
        self.cache = {}

    def call(self, *args):
        lookup = hash(args)
        if lookup in self.cache:
            return self.cache[lookup]
        else:
            value = self.callback(*args)
            self.cache[lookup] = value
            return value   