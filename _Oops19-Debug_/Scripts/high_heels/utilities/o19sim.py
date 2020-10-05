#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#


from high_heels.enums.constants import Oops19Constants
from typing import Union
import services
from high_heels.utilities.helper_standalone import O19Helper
from objects import ALL_HIDDEN_REASONS
from sims.sim import Sim
from sims.sim_info import SimInfo


class O19SimV2:
    '''
    A simple class to access all Sim properties and to retrieve them.
    o19sim = O19Sim(init)
    sim: Sim = o19sim.sim  # == o19sim._get_sim()
    sim_id: SimInfo = o19sim.sim_id  # == o19sim._get_sim_id()
    sim_info: SimInfo = o19sim.sim_info  # == o19sim._get_sim_info()
    sim_name: str = o19sim.sim_name  # == o19sim._get_sim_name()
    sim_filename: str = o19sim.sim_filename  # == o19sim._get_sim_filename()
    '''
    def __init__(self, p_sim: Union[None, Sim, int, SimInfo, str]):
        self.__init()
        self._sim = None
        self._sim_id = None
        self._sim_info = None
        self._sim_name = None
        self._sim_filename = None
        self._search_query = None

        if p_sim is None:
            client = self._client_mgr.get_first_client()
            self._sim: Sim = client.active_sim
            self._sim_info: SimInfo = client.active_sim_info
            self._sim_id: int = self._sim_info.id

        elif isinstance(p_sim, Sim):
            self._sim: Sim = p_sim
            self._sim_id: int = self._sim.sim_id

        elif isinstance(p_sim, int):
            self._sim_id: int = p_sim

        elif isinstance(p_sim, SimInfo):
            self._sim_info: SimInfo = p_sim
            self._sim_id: int = self._sim_info.id

        elif isinstance(p_sim, str):
            if Oops19Constants.SIM_NAME_SEP in p_sim:
                self._search_query: str = p_sim
            else:
                errmsg = f'To search by name add {Oops19Constants.SIM_NAME_SEP} to the search term.'
                raise ValueError(errmsg)
        else:
            errmsg = f'Unexpected type {type(p_sim)} received.'
            raise ValueError(errmsg)

    # noinspection PyBroadException
    @classmethod
    def __init(cls):
        try:
            cls._client_mgr
        except:
            cls._client_mgr = services.client_manager()
        try:
            cls._sim_info_mgr
        except:
            cls._sim_info_mgr = services.sim_info_manager()
        try:
            cls.oh
        except:
            cls.oh = O19Helper()

    def _set_sim_filename(self):
        """
        Sets the sim filename, by replacing all unsafe characters. 'C:\temp\' will become 'C__temp_'
        f(self._sim_name)
        """
        if not self._sim_name:
            self._set_sim_name()
        self._sim_filename = self.oh.get_sim_filename(self._sim_name)

    def _set_sim_name(self):
        """
        Sets the sim name, by joining first and last name with a '#'. '#' is not allowed in sim names and thus easy to split.
        f(self._sim_info)
        """
        if not self._sim_info:
            self._set_sim_info()
        first_name = getattr(self._sim_info, 'first_name')
        last_name = getattr(self._sim_info, 'last_name')
        self._sim_name = f"{first_name}{Oops19Constants.SIM_NAME_SEP}{last_name}"

    def _set_sim(self):
        """
        Set sim (self._sim)
        f(self._sim_info)
        """
        if not self._sim_info:
            self._set_sim_info()
        self._sim: Sim = self._sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        pass

    def _set_sim_info(self):
        """
        Set sim_info (self._sim_info)
        f(self._sim_info)
        """
        if not self._sim_id:
            self._set_sim_id()
        self._sim_info: SimInfo = self._sim_info_mgr.get(self.sim_id)

    def _set_sim_id(self):
        """
        Set sim_id (self._sim_id)
        f(self._search_query)
        If sim_id is not available the search query has to be used.
        """
        self._search_sim_name()
        first_name, last_name = self._sim_name.split(Oops19Constants.SIM_NAME_SEP, 1)
        self._sim_info: SimInfo = self._sim_info_mgr.get_sim_info_by_name(first_name, last_name)
        self._sim_id: int = self._sim_info.id

    def _search_sim_name(self):
        """
        Set sim_name (self._sim_name)
        f(self._search_query)
        """
        self._sim_name = self.oh.get_full_sim_name(self._search_query)

    # Public API to retrieve values
    @property
    def sim(self) -> Sim:
        if not self._sim:
            self._set_sim()
        return self._sim

    @property
    def sim_id(self) -> int:
        if not self._sim_id:
            self._set_sim_id()
        return self._sim_id

    @property
    def sim_info(self) -> SimInfo:
        if not self._sim_info:
            self._set_sim_info()
        return self._sim_info

    @property
    def sim_name(self) -> str:
        if not self._sim_name:
            self._set_sim_name()
        return self._sim_name

    @property
    def sim_filename(self) -> str:
        if not self._sim_filename:
            self._set_sim_filename()
        return self._sim_filename
