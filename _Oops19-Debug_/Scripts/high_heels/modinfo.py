#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#


from sims4communitylib.mod_support.common_mod_info import CommonModInfo


class ModInfo(CommonModInfo):
    """ Mod info for the S4CL Sample Mod. """
    _FILE_PATH: str = str(__file__)

    @property
    def _name(self) -> str:
        return 'High_Heels'

    @property
    def _author(self) -> str:
        return 'Oops19'

    @property
    def _base_namespace(self) -> str:
        return 'high_heels'

    @property
    def _file_path(self) -> str:
        return ModInfo._FILE_PATH

