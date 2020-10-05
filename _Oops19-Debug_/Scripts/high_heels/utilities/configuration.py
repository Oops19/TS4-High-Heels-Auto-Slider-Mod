#
# LICENSE https://creativecommons.org/licenses/by-nc-nd/4.0/ https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#
# At 2021-01-01 the license shall be changed to https://creativecommons.org/licenses/by/4.0/
#

# A simple class to write python data structures within a dict() to a file and to read them back in.
# Configuration files may be python data structures making it easy to read and write them.
# Only objects which can be serialized may be written to a file.
# Complex objects have to be converted to 'primitives' with a wrapper. The wrapper should also re-create complex objects when reading the file.
#   'x_configuration' is the dict to store the complex objects for further access. The wrapper needs to update 'configuration' upon changes of it and vice-versa.

import ast
import os
import time

from sims4communitylib.mod_support.mod_identity import CommonModIdentity
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

add_element_testing = True  # May be set to False for production


class Configuration():
    def __init__(self, mod_identity: CommonModIdentity, _filename, load_configuration: bool = False, auto_save: bool = False, backup_id: str = ''):
        self.log: CommonLog = CommonLogRegistry.get().register_log(mod_identity.author, mod_identity.name)
        self.log.enable()
        self.log.debug("C.init(_filename=" + str(_filename) + ", load_configuration=" + str(load_configuration) + ", auto_save=" + str(auto_save) + ")")

        self.configuration: dict = {}
        self.x_configuration: dict = {}

        self.updated = time.time()
        self._filename = _filename
        self.backup_id = backup_id
        self.auto_save = auto_save

        if _filename != "":
            if load_configuration:
                self.is_initializing = True
                self.load_configuration()
                del self.is_initializing  # remove this temp. var
        self.log.debug("C.init(OK)")

    @staticmethod
    def print_pretty(fp, data: str, _indent: str = '    '):
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

    def save_configuration(self) -> bool:
        self.updated = time.time()
        if self.is_initializing:
            return

        try:
            self.log.debug("C.save_configuration()")
            _filename = self._filename
            if self.backup_id != '':
                try:
                    os.remove(_filename + '.' + self.backup_id)
                except:
                    pass
                try:
                    os.rename(_filename, _filename + "." + self.backup_id)
                except:
                    pass
            self.log.debug("C.save_configuration() Writing: " + _filename)
            _configuration = self.configuration
            with open(_filename, 'wt') as fp:
                self.print_pretty(fp, str(_configuration))
                fp.close()

            return True
        except Exception as ex:
            self.log.debug("C.save_configuration() Error saving ini file: " + str(ex))
            raise

    def load_configuration(self) -> bool:
        self.updated = time.time()
        try:
            self.log.info("C.load_configuration()")
            _filename = self._filename
            if os.path.isfile(_filename):
                self.log.info("C.load_configuration() Reading: " + _filename)
                with open(_filename, 'rt') as fp:
                    configuration_text = ""
                    for line in fp:
                        configuration_text = configuration_text + line
                    fp.close()
                self.log.debug("C.load_configuration() Converting data: '" + str(configuration_text) + "'")
                self.configuration = ast.literal_eval(configuration_text)
                return True
            else:
                return False
        except Exception as ex:
            self.log.debug("C.load_configuration() Error loading ini file: " + str(ex))
            raise

    def get_configuration(self) -> []:
        try:
            self.log.debug("C.get_configuration()")
            return [self.configuration, self.x_configuration]
        except Exception as ex:
            self.log.debug("C.get_configuration() Error: " + str(ex))
            raise

    def _do_not_use_get_elements(self, element_id: int) -> []:
        try:
            self.log.debug("C._do_not_use_get_elements(" + str(element_id) + ")")
            return [self.configuration.get(element_id), self.x_configuration.get(element_id)]
        except Exception as ex:
            self.log.debug("C._do_not_use_get_elements() Error: " + str(ex))
            raise

    def get_element(self, element_id: int, x_config: bool = False) -> {}:
        try:
            self.log.debug("C.get_element(" + str(element_id) + ", " + str(x_config) + ")")
            if x_config:
                return self.x_configuration.get(element_id)
            return self.configuration.get(element_id)
        except Exception as ex:
            self.log.debug("C.get_element() Error: " + str(ex))
            raise

    def update_conf_element(self, element_id: int, element_data: dict, x_config: bool = False) -> {}:
        try:
            self.log.debug("C.update_configuration(" + str(element_id) + ", " + str(x_config) + ")")
            x_configuration = {} # Avoid 'Might be referenced before assignment warning' in return statement
            configuration = {} # Avoid 'Might be referenced before assignment warning' in return statement
            if x_config:
                _cfg: dict = self.x_configuration.get(element_id)
            else:
                _cfg: dict = self.configuration.get(element_id)
            _cfg.update(element_data)
            self._cfg.update({element_id: _cfg})
            self.save_configuration()
            return _cfg
        except Exception as ex:
            self.log.error("C.update_conf_element() Error")
            raise

    def add_element(self, element_id: int, element_data: object = None, x_element_data: object = None) -> bool:
        """
        :param element_id: required
        :param element_data: Set to 'None' will skip the element. It will not be set to 'None'
        :param x_element_data: Set to 'None' will skip the element. It will not be set to 'None'
        :return:
        """
        try:
            self.log.debug("C.add_element(id=" + str(element_id) + ", data=" + str(element_data) + ", x=" + str(x_element_data) + ")")
            if element_data is not None:
                self.configuration.update({element_id: element_data})

                if add_element_testing:
                    try:
                        element_data_text = element_data.__str__()
                        element_data_2 = ast.literal_eval(element_data_text)
                        if element_data != element_data_2:
                            self.log.error("C.add_element() Element " + str(element_id) + ": '" + str(element_data) + "' doesn't match '" + str(element_data_2) + "'.")
                    except Exception as ex:
                        self.log.error("C.add_element() Element " + str(element_id) + ": '" + str(element_data) + "' can not be saved." + str(ex))

                self.save_configuration()

            if x_element_data is not None:
                self.x_configuration.update({element_id: x_element_data})

            return True
        except Exception as ex:
            self.log.debug("C.add_element() Error: " + str(ex))
            raise

    def del_element(self, element_id: int) -> bool:
        try:
            self.log.debug("C.del_element(" + str(element_id) + ")")
            del self.configuration[element_id]
            del self.x_configuration[element_id]

            self.save_configuration()
            return True
        except Exception as ex:
            self.log.debug("C.del_element() Error: " + str(ex))
            raise

    def get_update_time(self) -> float:
        return self.updated