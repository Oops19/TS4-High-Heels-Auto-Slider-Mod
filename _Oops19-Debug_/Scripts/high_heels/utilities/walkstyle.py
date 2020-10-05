#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

from weakref import WeakKeyDictionary

import routing
import sims4.commands
import sims4.hash_util
import sims4.resources
import sims4.resources
from routing.walkstyle.walkstyle_request import WalkStyleRequest
from routing.walkstyle.walkstyle_tuning import Walkstyle
from sims.sim import Sim
from sims4.math import MAX_INT32


# random name to make sure that it does not collide with routing.walkstyle.walkstyle_tuning.Walkstyle
class Oops19Walkstyle():
    def __init__(self):
        self.__init()

    @classmethod
    def __init(cls):
        try:
            cls._walk_style_requests
        except:
            # Weak list to store all active walk styles
            cls._walk_style_requests = WeakKeyDictionary()
        try:
            cls.styles
        except:
            cls.styles = cls.__initialize_styles()

    @staticmethod
    def __initialize_styles() -> dict:
        styles = dict()
        for walkstyle in sims4.resources.list(type=sims4.resources.Types.WALKSTYLE):
            walkstyle = routing.get_walkstyle_name_from_resource(walkstyle)
            styles.update({int(sims4.hash_util.hash32(walkstyle)): walkstyle})
        return styles

    def set(self, sim: Sim, walkstyle_hash: int, priority: int = MAX_INT32) -> bool:
        try:
            if priority == -1:
                priority = MAX_INT32
            walkstyle_name = self.styles.get(walkstyle_hash)
            walkstyle = Walkstyle(walkstyle_name, walkstyle_hash)

            walkstyle_request = WalkStyleRequest(sim, walkstyle=walkstyle, priority=priority)
            walkstyle_request.start()

            self._walk_style_requests[sim] = walkstyle_request
            return True
        except Exception as ex:
            return False

    def stop(self, sim: Sim) -> bool:
        try:
            walkstyle_request = self._walk_style_requests.get(sim)
            if walkstyle_request is not None:
                walkstyle_request.stop()
                del _walk_style_requests[sim]
            return True
        except Exception as ex:
            return False

    def reset(self, sim: Sim, clean_cleanup: bool = False) -> bool:
        global _walk_style_requests
        try:
            # Try a clean 'reset' - Stop the current work style
            self.stop(sim)

            # Remove all walk styles assigned by the game to the sim
            __walk_style_requests = sim.routing_component.get_walkstyle_requests()
            if clean_cleanup:
                for walkstyle_request in __walk_style_requests:
                    walkstyle_request.stop()
                del __walk_style_requests[sim]

            # Clear all walkstyles for this sim in case there are still some.
            __walk_style_requests.clear()
            return True
        except:
            # Oops! This didn't work. Clear the list anyway.
            __walk_style_requests = sim.routing_component.get_walkstyle_requests()
            __walk_style_requests.clear()
            return False

    def get_walk_styles(self, walkstyle_filter : str = None) -> {}:
        _styles = dict()
        try:
            __styles = dict()
            if walkstyle_filter:
                l_walkstyle_filter = walkstyle_filter.lower()
            else:
                l_walkstyle_filter = None  # to avoid the warning that this variable may be unassigned
            for hash32, walkstyle in self.styles.items():
                if not walkstyle_filter or l_walkstyle_filter in walkstyle.lower():
                    __styles.update({hash32: walkstyle})
            _styles = __styles
        except:
            pass
        return _styles