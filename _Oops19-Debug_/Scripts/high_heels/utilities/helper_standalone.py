#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

from typing import Union, List
import services
from high_heels.enums.constants import Oops19Constants
from high_heels.enums.hh_constants import HighHeelsConstants

from objects import ALL_HIDDEN_REASONS
from sims.sim import Sim
from sims.sim_info import SimInfo
import re

sim_names = {}
sim_ids = {}


class O19Sim:
    def __init__(self, sim, sim_id, sim_info, sim_name, sim_filename):
        self.sim = sim
        self.sim_id = sim_id
        self.sim_info = sim_info
        self.sim_name = sim_name
        self.sim_filename = sim_filename

class O19Helper:
    '''
    Gernaral usage:
    oh = None
    def foo():
        global oh
        if not oh:
            oh = O19Helper() || oh = O19Helper(output) when using the cheat console / debugging.


        # Get the sim, sim_info and other sim information.
        # S4CL has methods to fetch single values which should be used in production.
        sim, sim_id, sim_info, first_name, last_name = oh.get_sim_all(None || sim || sim_id || sim_info || sim_name)
        Parameters:
        None: The active sim will be used.
        int(sim_id): The sim matching the sim_id will be used.
        str(sim_id): The sim matching the sim_id will be used.
            str(sim_id) does not need to be complete, it is expanded as needed. '1' will usually return a random sim. At least 4 digits should be used.
        Sim(sim): The sim matching the sim object will be used.
        SimInfo(sim_info): The sim matching the sim_info object will be used.
        str(sim_first_name + "#" + sim_last_name): Special case, first and last name must be attached with '#' (unsupported char in a sim name but fine in cheat console).
            Neither sim_first_name nor sim_last_name have to be full strings, they are expanded as needed. '#' will usually return a random sim.


        # Log a message to console or to the S4CL logger.
        oh.log('message') || oh.log('message', exception)

    '''

    def __init__(self, output=None, verbose=False):
        self.verbose = verbose
        self.output = output
        self.log(f"O19Helper.__init__(output={str(output)[0: 15]}, verbose={verbose})")

    def get_sim_name(self, first_name: str = '', last_name: str = '') -> str:
        """
        Returns the sim name, by joining first and last name with a '#'. '#' is not allowed in sim names and thus easy to split.
        :param last_name:
        :return:
        """
        return f"{first_name}{Oops19Constants.SIM_NAME_SEP}{last_name}"

    def split_sim_name(self, sim_name: str = '#') -> []:
        """
        Returns the sim name, by joining first and last name with a '#'. '#' is not allowed in sim names and thus easy to split.
        :param last_name:
        :return:
        """
        return sim_name.split(Oops19Constants.SIM_NAME_SEP, 1)

    def get_sim_filename(self, sim_name: str = ''):
        a = re.sub(Oops19Constants.INVALID_FILENAME_CHARACTERS, Oops19Constants.SIM_FILENAME_SPACE, sim_name)
        return re.sub(Oops19Constants.INVALID_FILENAME_CHARACTERS, Oops19Constants.SIM_FILENAME_SPACE, sim_name)

    def log(self, message: str = '', exception: Union[Exception, None] = None):
        try:
            if self.output:
                if exception:
                    self.output(message + ' ' + str(exception))
                else:
                    self.output(message)
            else:
                from high_heels.modinfo import ModInfo
                from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
                log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity().author, ModInfo.get_identity().name)
                log.enable()
                if exception:
                    log.error(message, exception=exception)
                else:
                    log.debug(message)
        except Exception as ex:
            # Obviously we can not log, discard this exception unless verbose
            if self.verbose:
                raise ex

    def get_sim_all(self, p_sim: Union[None, int, str, Sim, SimInfo], log=True) -> O19Sim:
        '''
        Usage: o19sim: O19Sim = oh.get_sim_all('Bel#Go') # This should return Bella Goth
        :param p_sim: Parameter to specify the sim. Set to 'None' for the current sim. A sim_id(int), Sim or SimInfo object are also supported.
            A string may be used and contain the starting sim_id (eg str('123') - a random Sim starting with this sim_id will be selected.
            Or the sim name (str('FirstName1 FirstName2#LastName1 LastName2') or less characters like str('Fir#L') may be used. Also here a random Sim matching the strings will be selected.
        :param log: Optional parameter to supress logging.
        :return: O19Sim with these attributes: sim: Sim, sim_id: int, sim_info: SimInfo, str: sim_name, str:sim_filename.
        The sim_info may be None if the sim is active but not ready (off-lot).
        '''
        try:
            sim_info = None
            if log:
                self.log(f"get_sim_all({p_sim} :{type(p_sim)}, ...)")
            if isinstance(p_sim, str) and (not p_sim.isdigit()) and (not Oops19Constants.SIM_NAME_SEP in str(p_sim)):  # String supplied which can not be converted to a number but missing '#'
                p_sim = f"{p_sim}#"  # Attach a hash, string will be used as first name
            if p_sim is None:
                client = services.client_manager().get_first_client()
                sim: Sim = client.active_sim
                sim_info: SimInfo = client.active_sim_info
                sim_id: int = sim_info.id
                first_name = getattr(sim_info, 'first_name')
                last_name = getattr(sim_info, 'last_name')
            elif Oops19Constants.SIM_NAME_SEP in str(p_sim):  # p_sim contains '#'
                sim_name = self.get_full_sim_name(p_sim)
                first_name, last_name = str(sim_name).split(Oops19Constants.SIM_NAME_SEP, 1)
                sim_info: SimInfo = services.sim_info_manager().get_sim_info_by_name(first_name, last_name)
                sim_id: int = sim_info.id
                sim: Sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            else:
                if isinstance(p_sim, Sim):
                    sim_id = p_sim.sim_id
                elif isinstance(p_sim, SimInfo):
                    sim_id = p_sim.id
                elif isinstance(p_sim, str):
                    global sim_ids
                    if not sim_ids:
                        self.init_name_cache()
                        a = self.expand_string(p_sim, sim_ids)
                    try:
                        sim_id = int(self.expand_string(p_sim, sim_ids))  # None may be returned, expect int(None)
                    except:
                        # avoid exception during initialization
                        return O19Sim(None, -1, None, '', '')
                elif isinstance(p_sim, int):
                    sim_id = p_sim
                else:
                    raise NotImplementedError
                sim_info: SimInfo = services.sim_info_manager().get(sim_id)
                if not sim_info:
                    # avoid exception during ini _tialization
                    return O19Sim(None, -1, None, '', '')
                sim: Sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                first_name = getattr(sim_info, 'first_name')
                last_name = getattr(sim_info, 'last_name')
            sim_name = self.get_sim_name(first_name, last_name)
            sim_filename = self.get_sim_filename(sim_name)
            o19sim = O19Sim(sim, sim_id, sim_info, sim_name, sim_filename)
            if sim is None:
                sim_info: SimInfo = services.sim_info_manager().get(sim_id)  # not the same as services.sim_info_manager().get_sim_info_by_name(first_name, last_name)
                sim: Sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            self.log(f"rv: get_sim_all() {type(sim)} {sim_id}:{type(sim_id)} {type(sim_info)} {sim_name}{type(sim_name)} {type(sim_filename)}")
            return o19sim
        except Exception as ex:
            self.log("get_sim_all() Error: ", ex)
        return O19Sim(None, -1, None, '', '')

    def print_pretty(self, fp, data: str, _indent: str = '    '):
        default_indent: str = _indent
        indent: str = ""
        i: int = 0
        for line in data.replace('{', '{\n').replace('}', '\n}').replace(', ', ',\n').splitlines():
            if line.startswith('}'):
                i = i - 1
                indent = default_indent * i
            fp.write(indent + line + "\n")
            if line.endswith('{'):
                i = i + 1
                indent = default_indent * i

    def init_name_cache(self) -> dict:
        global sim_ids, sim_names
        _sim_ids = {}
        _sim_names = {}
        try:
            all_sims: dict = services.sim_info_manager().get_all()
            self.log(f'Processing {len(all_sims)} sims.')
            for sim_info in all_sims:
                if sim_info is None:
                    continue
                break
            for sim_info in all_sims:
                #sim, sim_id, sim_info, first_name, last_name = self.get_sim_all(sim, log=False)
                o19sim: O19Sim = self.get_sim_all(sim_info, log=True)
                first_name, last_name = o19sim.sim_name.split(Oops19Constants.SIM_NAME_SEP, 1)
                _sim_names.update({o19sim.sim_id: self.get_sim_name(first_name.lower(), last_name.lower())})
                _sim_ids.update({str(o19sim.sim_id): str(o19sim.sim_id)})  # FIXME - k = v to use the dict for expansion
            sim_names = _sim_names
            sim_ids = _sim_ids

        except Exception as ex:
            self.log("init_name_cache() Error: ", ex)
        return _sim_names

    def get_full_sim_name(self, sim_name: str = None) -> Union[str, None]:
        """
        :param sim_name: A sim name in the 'normalized' sim_name form (first and last name joind with '#'.
        '#' is required and will return a random name (eg: Ann Smith)
        'a#' will return a first name starting, ending or containing an 'a' (eg: Ann Smith)
        '#s' will return a last name starting, ending or containing an 's' (eg: Ann Smith)
        'aget_sim_all#s' will return a sim with an 'a' in the first name and and 's' in the last name (e.g. Ann Smith, Ali Shi)
        'a#s' may return 'Ann Smith' first (startswith), if this fails then 'Bella Miss' (endswith), and if this also fails 'Tam Isa' (contains).
            If also the last check fails None is returned. This may happen quite often if you enter non-ascii strings while your sims have ascii names or vice versa.
        :return: 'Normalized' sim name (sim_name).
        """
        global sim_names
        try:
            if (not sim_name) or (HighHeelsConstants.SIM_NAME_SEP not in sim_name):
                return None
            if not sim_names:
                self.init_name_cache()
            short_first_name, short_last_name = str(sim_name).lower().split(HighHeelsConstants.SIM_NAME_SEP, 1)

            self.log(f"Searching '{short_first_name}' '{short_last_name}' in {len(sim_names)} entries.")
            search = True
            # 1st try match startswith
            if search:
                for sim_id, sim_name in sim_names.items():
                    first_name, last_name = self.split_sim_name(sim_name)
                    if first_name.startswith(short_first_name) and last_name.startswith(short_last_name):
                        self.log(f"{first_name}={short_first_name} & {last_name}={short_last_name}")
                        search = False
                        break
            # 2nd round - match endswith
            if search:
                for sim_id, sim_name in sim_names.items():
                    first_name, last_name = self.split_sim_name(sim_name)
                    if first_name.endswith(short_first_name) and last_name.endswith(short_last_name):
                        search = False
                        break
            # 3rd round - match contains
            if search:
                for sim_id, sim_name in sim_names.items():
                    first_name, last_name = self.split_sim_name(sim_name)
                    if short_first_name in first_name and short_first_name in last_name:
                        search = False
                        break

            if search:
                self.log("Found nothing.")
                return None

            return first_name + Oops19Constants.SIM_NAME_SEP + last_name

        except Exception as ex:
            self.log("get_full_name() Error: ", ex)
        return None

    def expand_string(self, p_key: str = '', p_values: dict = {}, lookup: bool = True, starts_with: bool = True, ends_with: bool = False, contains: bool = False, case_sensitive: bool = False) -> Union[str, None]:
        """
        A simple method to allow to specify an abbr. in the cheat console. Not 100% case insensitive. If possible use lower case keys
        :param p_key: String to be replaced with dict key or value.
        :param p_values: Dict with key value pairs.
        :return: The full string or None if nothing was found.
        """
        self.log(f"expand_string({p_key}, {p_values}, ...")
        l_key = None
        l_values = {}
        m_values = {}
        if not case_sensitive:
            l_key = p_key.lower()
            l_values = {k.lower(): v.lower()
                for k, v in p_values.items()
            }
            m_values = {v.lower(): v
                for v in p_values.values()
            }

        # 1 - p_key is already expanded
        if l_key:
            if l_key in l_values.values():
                return m_values.get(l_key)
        else:
            if p_key in p_values.values():
                return p_key

        # 2 - [pl]_key matches key in [pl]_values
        if lookup:
            if l_key:
                if l_key in l_values.keys():
                    m_key = l_values.get(l_key)
                    return m_values.get(m_key)
                else:
                    if p_key in p_values.keys():
                        return p_values.get(p_key)

        # 3 - starts_with check
        if starts_with:
            if l_key:
                for v in l_values.values():
                    if v.startswith(l_key):
                        return m_values.get(v)
            else:
                for v in p_values.values():
                    if v.startswith(p_key):
                        return v

        # 4 - ends_with
        if ends_with:
            if l_key:
                for v in l_values.values():
                    if v.ends_with(l_key):
                        return m_values.get(v)
            else:
                for v in p_values.values():
                    if v.ends_with(p_key):
                        return v

        # 5 - contains
        if contains:
            if l_key:
                for v in l_values.values():
                    if v.contains(l_key):
                        return m_values.get(v)
            else:
                for v in p_values.values():
                    if v.contains(p_key):
                        return v

        return None

    def write_to_console(self, output, header: str = '', values: Union[dict, list, set, str] = None, p_filter_str: str = '', split_str: str = ' ', length_linebreak: int = 102, max_values_per_line: int = 1000) -> []:
        if output:
            lines = self._trim_to(header, values, p_filter_str, split_str, length_linebreak)
            for line in lines:
                output(line)

    def _trim_to(self, header: str = '', values: Union[dict, list, set, str] = None, p_filter_str: str = '', split_str: str = ' ', length_linebreak: int = 1024, max_values_per_line: int = 1000) -> []:
        '''
        :param output: The 'Cheat output console'
        :param header: The 1st line to print. It's not modified.
        :param values: The data will be printed in lines not longer than 'length_linebreak' (unless the values itself are not longer).
        :param p_filter_str: Content can be filtered. 'a' will display only data containing [aA]. It has no effect for instanceof(values, str).
        :param split_str: Set this for instanceof(values, str) to split the string as desired. Otherwise not used.
        :param length_linebreak: The TS4 cheat console supports 1024? characters for each output() call. To avoid missing chars to not set higher.
        :param max_values_per_line: Limit the number of parameters per line.
        :return: Array with the data to print
        '''
        lines = []
        filter_str = f"{p_filter_str}".lower()
        if header:
            lines.append(f"{header}")
            # lines.append(f"{header:.{length_linebreak}s}")  # Trim header - Likely not desired if length_linebreak is set to a low value
        if isinstance(values, dict):
            elements = {}
            for key, value in values.items():
                if filter_str and ((filter_str in key.lower()) or (filter_str in value.lower())):
                    continue
                new_elements = {**elements, **{key: value}}
                if (len(f"{new_elements}") > length_linebreak) or (len(elements) > max_values_per_line):
                    if elements:
                        lines.append(f"{elements}")
                        elements = {}
                    else:
                        elements = new_elements
            if elements:
                lines.append(f"{elements}")
        elif isinstance(values, list) or isinstance(values, tuple) or isinstance(values, set):
            elements = set()  # avoid duplicates in the same output line
            for element in values:
                if filter_str and (filter_str not in element.lower()):
                    continue
                new_elements = elements | {element}
                if (len(f"{new_elements}") > length_linebreak) or (len(elements) > max_values_per_line):
                    if elements:
                        lines.append(f"{elements}")
                        elements = set()
                    else:
                        elements = new_elements
            if elements:
                lines.append(f"{elements}")
        elif isinstance(values, str):
            elements = ''
            counter = 1
            for element in values.split(split_str):
                if elements:
                    new_elements = f"{elements}{split_str}{element}"
                else:
                    new_elements = element  # 1st word only
                if (len(f"{new_elements}") > length_linebreak) or (counter > max_values_per_line):
                    lines.append(elements)
                    elements = element
                    counter = 1
                else:
                    elements = new_elements
                    counter += 1
            lines.append(elements)
        return lines
