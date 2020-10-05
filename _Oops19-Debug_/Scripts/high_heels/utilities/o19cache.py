#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

# Warning: This cache does not work as expected. Do NOT use.

from typing import Union
from weakref import WeakKeyDictionary


class O19Cache:
    """
    Usage pattern for cache:
        o19cache = O19Cache()
        o19sim = O19Sim(p_sim)
        o19sim = o19cache.get(sim)  # May return None !
        o19cache.add(sim, o19sim)
    """
    def __init__(self):
        self.__init()

    @classmethod
    def __init(cls):
        try:
            cls.cache
        except:
            cls.cache = WeakKeyDictionary()
            #cls.cache.g
    def add(self, obj, data):
        self.cache.update({obj: data})
        #self.cache[obj] = data

    def get(self, obj) -> Union[None, object]:
        return self.cache.get(obj)


    # Not implemented to avoid dependencies:
    # def add(self, sim: Sim, o19sim: O19Sim):
        # self.cache[sim] = o19sim
    # def get(self, sim) -> Union[None, o19sim]:
        # o19sim = self.cache[sim]
        # return o19sim