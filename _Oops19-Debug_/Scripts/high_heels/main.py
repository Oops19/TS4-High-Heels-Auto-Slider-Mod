#
# LICENSE https://creativecommons.org/licenses/by-nc-nd/4.0/ https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#
# At 2021-01-01 the license shall be changed to https://creativecommons.org/licenses/by/4.0/
#

import ast
import os
import time
from os import path
from typing import Union

import services
import sims4
import sims4.commands
from high_heels.enums.constants import Oops19Constants
from high_heels.enums.hh_constants import HighHeelsConstants

from high_heels.modinfo import ModInfo
from high_heels.utilities.helper_standalone import O19Helper, O19Sim
from high_heels.utilities.walkstyle import Oops19Walkstyle
from objects import ALL_HIDDEN_REASONS
from protocolbuffers import PersistenceBlobs_pb2
from protocolbuffers.PersistenceBlobs_pb2 import BlobSimFacialCustomizationData
from sims.outfits.outfit_enums import OutfitCategory
from sims.sim import Sim
from sims.sim_info import SimInfo
from sims.sim_info_base_wrapper import SimInfoBaseWrapper
from sims4communitylib.utils.common_injection_utils import CommonInjectionUtils
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
from sims4communitylib.utils.resources.common_interaction_utils import CommonInteractionUtils
from sims4communitylib.utils.sims.common_sim_interaction_utils import CommonSimInteractionUtils

oh = None

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity().author, ModInfo.get_identity().name)

# global variables - some are used, some are only set but never read.
preset_configuration = {}  # The parsed configuration of all "presets.*.ini" files

preset_configuration_ids = set()  # int - all configuration preset IDs
preset_configuration_cas_ids = set()  # int - all cas IDs
preset_configuration_blacklist_interaction_ids = set()  # int - use default settings if interaction is running
preset_configuration_blacklist_sim_ids = set()  # int - skip all sims in this set

preset_configuration_body_types = set()  # int - all used body type, for shoes only: {8}
preset_configuration_modifier_ids = set()  # int - all used modifier IDs, likely {2} or {1, 2}
preset_configuration_face_sliders_ids = set()  # int - all used face sliders IDs
preset_configuration_body_sliders_ids = set()  # int - all used body sliders IDs

preset_body_type_2_face_sliders = dict()  # int - face sliders used for a specific body part {8: (11, 22, 33), 10: (33, 55, 66)}
preset_body_type_2_body_sliders = dict()  # int - body sliders used for a specific body part {8: (1, 2, 3), 10: (3,5,6)}

preset_cas_ids_2_id = dict()  # int - configuration ids used for a cas item
preset_id_2_face_sliders = dict()  # int - face sliders used for a configuration id {10: {1: 1.0, 2: 0.2, 3: 0.3}, 20: [1: 0.1, 3: 0.3}}
preset_id_2_body_sliders = dict()  # int - body sliders used for a configuration id {10: {11: 1.0, 22: 0.2, 33: 0.3}, 20: [11: 0.1, 33: 0.3}}
preset_id_2_walkstypes = dict()  # int - walk style  for a configuration id {10: {123: 33}, 20: {444: 44}}


# On_load: Update all sim_default_values if a new ID was added
# If shoe is detected get the SIM_ID and store all relevant slider values if not yet in 'sim_default_values'
# If shoe is not detected and SIM_ID in 'sim_default_values' apply these slider values
# If shoe is not detected and SIM_ID is not in 'sim_default_values' nothing happens
modified_sims = set()  # A list with all sims in sim_default_values
sim_default_values: Union[dict, None] = None  # A set with all default slider values for all sims (containing only the used sliders)

# The structure looks like this
sample_default_values = {
    # sim_id: {
        # slider_id: slider_value,  slider_id: slider_value, ...
    # },
    11: {  # simID
        1234: 0.0, 44444: 0.3, 999999: 0.8, 55555: 0.0, 33333: 0.0  #
    },
}


@CommonInjectionUtils.inject_safely_into(ModInfo.get_identity(), SimInfoBaseWrapper, SimInfoBaseWrapper._set_current_outfit_without_distribution.__name__)
def hh_set_current_outfit_without_distribution(original, self, *args, **kwargs):
    change_clothes(self, *args, **kwargs)
    return original(self, *args, **kwargs)


def change_clothes(_self, *args, **kwargs):
    main = HighHeels()
    main.change_clothes(_self, *args, **kwargs)


previous_change_time = 0
previous_sim_id = -1
log_trace = False
o19ws = None


class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class HighHeels(Borg):
    def __init__(self):
        Borg.__init__(self)
        self.__init()

    def __init(self):
        global log, sim_default_values, o19ws
        if sim_default_values is None:  # {} is a valid value
            log.enable()
            log.info("Main.init()")
            self.read_ini_files()
            sim_default_values = self.read_config_file(sim_default_values)
            o19ws = Oops19Walkstyle()


    def slide_to2(self, sim_info: SimInfo = None, modifier_type: int = -1, slider_id: int = -1, slider_value: Union[float, None] = None):
        log.debug(f"slide_to(SimInfo, {modifier_type}, {slider_id}, {slider_value})")
        if (SimInfo is None) or (modifier_type < 1) or (modifier_type > 2) or (slider_id < 0):
            log.error("Invalid parameters")
            return
        try:
            appearance_attributes = PersistenceBlobs_pb2.BlobSimFacialCustomizationData()
            appearance_attributes.MergeFromString(sim_info.facial_attributes)
            found_modifier = False
            if modifier_type == HighHeelsConstants.BLOB_SIM_BODY_MODIFIER:
                modifiers = appearance_attributes.body_modifiers
            else:
                modifiers = appearance_attributes.face_modifiers

            for modifier in modifiers:
                if modifier.key == slider_id:
                    log.debug(f"Modifier found")
                    found_modifier = True
                    break

            if not found_modifier:
                if slider_value is None:
                    return False  # Modifier not found and no new value specified
                # Add slider (hopefully it exits in-game)
                log.info(f"Modifier not found ... adding it on-the-fly")
                modifier = BlobSimFacialCustomizationData.Modifier()
                modifier.key = slider_id  # set key & value
                modifier.amount = slider_value
                if modifier_type == HighHeelsConstants.BLOB_SIM_BODY_MODIFIER:
                    appearance_attributes.body_modifiers.append(modifier)
                else:
                    appearance_attributes.face_modifiers.append(modifier)
                sim_info.facial_attributes = appearance_attributes.SerializeToString()
                sim_info.resend_facial_attributes()
                return True  # Slider added and set

            # Modifier found
            current_value = modifier.amount
            if slider_value is not None:  # Check for None. '0' is not None. But 'if 0' == 'if None'.
                modifier.amount = slider_value

                sim_info.facial_attributes = appearance_attributes.SerializeToString()
                sim_info.resend_facial_attributes()
            return current_value

        except Exception as ex:
            log.error("slide_to() Error", ex)
        return -1

    def change_clothes(self, _sim_info: SimInfo, *args, **kwargs):
        # The 1st block makes sure that a valid sim_info is set and that we don't call it too often.
        global log, previous_change_time, previous_sim_id
        try:
            sim_id: int = _sim_info.id
            sim_info: SimInfo = services.sim_info_manager().get(sim_id)  # TODO Create instance only once ? Or skip completely?
            sim: Sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        except:
            return
        # Here we have hopefully a valid sim_info object
        if (sim_id == previous_sim_id) and (previous_change_time >= time.time()):
            # event is triggered often, one time in 3s for each sim is allowed (even more if sims are switched fast enough)
            return
        previous_sim_id = sim_id
        previous_change_time = time.time() + 3

        # Real start of change_clothes
        log.debug(f"change_clothes({sim_id})")

        global preset_configuration, preset_configuration_body_types, preset_body_type_2_face_sliders, preset_body_type_2_body_sliders
        global sim_default_values, modified_sims, preset_configuration_cas_ids
        global preset_cas_ids_2_id, preset_id_2_face_sliders, preset_id_2_body_sliders
        global log_trace, o19ws
        if not preset_configuration:
            log.debug("Aborting as config is missing.")
            return False

        if sim_id in preset_configuration_blacklist_sim_ids:
            log.debug(f"Skipping sim ({HighHeelsConstants.PRESET_CFG_BL_SIM})")
            return False

        reset_to_default = False

        # TODO Add mod.ini and configure it there. Allow even more than on ID
        ww_sex_interation_id = 11270438951712522986  # as seen as in enums.interactions_enum
        no_slider_ids = (ww_sex_interation_id,)

        # Iterate over all interactions and if one matches the blacklist set the sliders to default
        # A cloth change for this sim must happen as we do not intercept interactions.
        ri = CommonSimInteractionUtils.get_running_interactions_gen(sim_info)
        for interaction in ri:
            if CommonInteractionUtils.get_interaction_id(interaction) in no_slider_ids:
                reset_to_default = True
                log.debug(f"Sliders to default ({HighHeelsConstants.PRESET_CFG_BL_INTERACTION}).")

        # Parse the parameters of the original method and fetch the current outfit (-1[0]) should also work.
        try:
            outfit_category_and_index: tuple[OutfitCategory: int] = args[0]
            outfit_category: OutfitCategory = outfit_category_and_index[0]
            outfit_index: int = outfit_category_and_index[1]
            log.debug(f"Changing clothes: (sim_id outfit[index]): {sim_id} {outfit_category}[{outfit_index}]")
            outfit = sim_info.get_outfit(outfit_category, outfit_index)
        except Exception as ex:
            log.error("change_clothes(1) Error occurred.", exception=ex)
            return False

        # Iterate over all configured body_types. For shoes this is '8'
        # Fill 'body_type_2_outfit' with all matching {body_type: outfit_part_id} values
        body_type_2_outfit = {}
        try:
            for body_type in preset_configuration_body_types:
                # outfit.body_types[n] contains the body_type (PRESET_CFG_BODY_TYPE) with value n. outfit.body_types[8] is likely not 8 as this would be too easy.
                # outfit.part_ids[n] contains the outfit_part_id (PRESET_CFG_CAS)
                if body_type in outfit.body_types:
                    i = outfit.body_types.index(body_type)
                    outfit_part_id = outfit.part_ids[i]
                    body_type_2_outfit.update({body_type: outfit_part_id})
            log.debug(f"Clothing items: ({body_type_2_outfit})")
            if not body_type_2_outfit:
                return False
        except Exception as ex:
            log.error("change_clothes(2) Error occurred.", ex)
            return False

        # Iterate over body_type_2_outfit
        for body_type, outfit_part_id in body_type_2_outfit.items():
            if log_trace:
                log.debug(f"Processing {HighHeelsConstants.PRESET_CFG_BODY_TYPE}/outfit_part_id for all {HighHeelsConstants.PRESET_CFG_CAS}: {body_type}/{outfit_part_id} for all {preset_configuration_cas_ids}")
            else:
                log.debug(f"Processing {HighHeelsConstants.PRESET_CFG_BODY_TYPE}/outfit_part_id for {HighHeelsConstants.PRESET_CFG_CAS} items: {body_type}/{outfit_part_id} for {len(preset_configuration_cas_ids)} items.")
            # Check if sim is new and/or sliders have to be adjusted
            try:
                if log_trace:
                    log.debug(f"    sim_id in modified_sims: {sim_id} in {modified_sims} ?")
                if outfit_part_id not in preset_configuration_cas_ids:
                    log.debug(f"    outfit_part_id not in {HighHeelsConstants.PRESET_CFG_CAS}")
                    reset_to_default = True
                    if sim_id not in modified_sims:
                        log.debug(f"    Sim sliders were never modified before, processing the next outfit_part_id right now.")
                        continue
                else:
                    # Sim wears an item which requires slider adjustments
                    if sim_id not in modified_sims:
                        log.debug(f"    Sim sliders were never modified before, saving the defaults now.")
                        self.store_sim_sliders(sim_id, sim_default_values)
            except Exception as ex:
                log.error(f"    change_clothes(3) Error occurred.", ex)
                return False

            # Porcess this  body_type/outfit_part_id and adjust the sliders
            try:
                # Code for face and body
                appearance_attributes = PersistenceBlobs_pb2.BlobSimFacialCustomizationData()  # doc: 'https://pydoc.net/botchallenge/1.2.0/google.protobuf.internal.cpp_message/'
                appearance_attributes.MergeFromString(sim_info.facial_attributes)  # NOT sim_info.bodily_attributes OR sim_info.appearance_attributes !

                #######################################################################################
                # Separate code for face (and body) - just in case we need to add a modifier.
                # Face should be empty, wearing heels or a bra does likely not shrink the nose, while in TS4 everything is possible.
                _face_sliders = preset_body_type_2_face_sliders.get(body_type)
                if _face_sliders:
                    face_sliders: list = list(_face_sliders)
                    log.debug(f"    {HighHeelsConstants.PRESET_CFG_FACE_MODIFIERS}: {face_sliders}")
                    slider_id_2_modifiers = {}
                    # Iterate over all messages and store them for later usage
                    for modifier in appearance_attributes.face_modifiers:
                        if modifier.key in face_sliders:
                            slider_id_2_modifiers.update({modifier.key: modifier})
                    log.debug(f"    Found these sliders: {slider_id_2_modifiers}")

                    for slider_id in face_sliders:
                        log.debug(f"    slider_id={slider_id}")
                        if slider_id not in slider_id_2_modifiers.keys():
                            # Add slider (hopefully it exits in-game) for the Sim
                            log.info(f"    face_modifier not found ... adding it on-the-fly")
                            modifier = BlobSimFacialCustomizationData.Modifier()
                            modifier.key = int(slider_id)  # set key & value
                            modifier.amount = 0
                            appearance_attributes.face_modifiers.append(modifier)

                        # Calculate the new slider value
                        slider_value = sim_default_values.get(sim_id).get(slider_id)
                        log.debug(f"    Default slider_value={slider_value}")
                        if not reset_to_default:
                            _slider_offset = 0
                            for _id in preset_cas_ids_2_id.get(outfit_part_id):
                                log.debug(f"    preset_id={_id}")
                                try:
                                    _slider_offset = preset_id_2_body_sliders.get(_id).get(slider_id)
                                    log.debug(f"    offset={_slider_offset}")
                                    if _slider_offset:
                                        slider_value = slider_value + _slider_offset
                                except Exception as ee:
                                    log.error("    id not found. This must never happen!", ee)

                            # relative adjustments in range [0..1]
                            if slider_value < 0:
                                slider_value = 0
                            elif slider_value > 1:
                                slider_value = 1

                        # Modify the slider
                        self.slide_to2(sim_info, HighHeelsConstants.BLOB_SIM_FACE_MODIFIER, slider_id, slider_value)
                        log.debug(f"    Set slider: {HighHeelsConstants.BLOB_SIM_FACE_MODIFIER} {slider_id} {slider_value}")

                #######################################################################################
                # Separate code for (face and) body - just in case we need to add a modifier.
                # Body modifiers (leg length, sim height, fly, ...)
                # preset_body_type_2_body_sliders ~ {5: {6248723735190925703, 6495998580922825632, 17028080069998725797}, 8: {3484085079657901585, 18312657795089936447}}
                # body_sliders ~ {3484085079657901585, 18312657795089936447}
                _body_sliders = preset_body_type_2_body_sliders.get(body_type)
                if _body_sliders:
                    body_sliders: list = list(_body_sliders)
                    log.debug(f"    {HighHeelsConstants.PRESET_CFG_BODY_MODIFIERS}: {body_sliders}")
                    slider_id_2_modifiers = {}
                    # Iterate over all messages and store them for later usage
                    for modifier in appearance_attributes.body_modifiers:
                        if modifier.key in body_sliders:
                            slider_id_2_modifiers.update({modifier.key: modifier})
                    log.debug(f"    Found these sliders: {slider_id_2_modifiers}")

                    for slider_id in body_sliders:
                        log.debug(f"    slider_id={slider_id}")
                        if slider_id not in slider_id_2_modifiers.keys():
                            # Add slider (hopefully it exits in-game) for the Sim
                            log.info(f"    body_modifier not found ... adding it on-the-fly")
                            modifier = BlobSimFacialCustomizationData.Modifier()
                            modifier.key = int(slider_id)  # set key & value
                            modifier.amount = 0
                            appearance_attributes.body_modifiers.append(modifier)

                        # Calculate the new slider value
                        slider_value = sim_default_values.get(sim_id).get(slider_id)
                        log.debug(f"    Default slider_value={slider_value}")
                        if slider_value is None:
                            slider_value = 0
                        if not reset_to_default:
                            _slider_offset = 0
                            for _id in preset_cas_ids_2_id.get(outfit_part_id):
                                log.debug(f"    preset_id={_id}")
                                try:
                                    # _slider_offset = preset_configuration.get(_id).get(HighHeelsConstants.PRESET_CFG_BODY_MODIFIERS).get(slider_id)
                                    _slider_offset = preset_id_2_body_sliders.get(_id).get(slider_id)
                                    log.debug(f"    offset={_slider_offset}")
                                    if _slider_offset:
                                        slider_value = slider_value + _slider_offset
                                except Exception as ee:
                                    log.error("    id not found. This must never happen!", ee)

                            # relative adjustments in range [0..1]
                            if slider_value < 0:
                                slider_value = 0
                            elif slider_value > 1:
                                slider_value = 1

                        self.slide_to2(sim_info, HighHeelsConstants.BLOB_SIM_BODY_MODIFIER, slider_id, slider_value)
                        log.debug(f"    Set slider: {HighHeelsConstants.BLOB_SIM_BODY_MODIFIER} {slider_id} {slider_value}")
                log.debug("    Sliders for this outfit_part_id adjusted")

                # Set the walkstyle
                if sim:
                    if not o19ws:
                        o19ws = Oops19Walkstyle()
                    if reset_to_default:
                        o19ws.stop(sim)
                    else:
                        all_walkstyles = {}
                        for _id in preset_cas_ids_2_id.get(outfit_part_id):
                            walkstyles = preset_id_2_walkstypes.get(_id)
                            if walkstyles:
                                all_walkstyles.update(walkstyles)
                        # all_walkstyles contains all configured walk styles. It may also be empty.
                        # TODO choose a random walkstyle. Using the 1st item and exiting atm
                        for walkstyle, priority in walkstyles.items():
                            o19ws.set(sim, walkstyle_hash=walkstyle, priority=priority)
                            break

            except Exception as ex:
                log.error("change_clothes(4) Error occurred.", exception=ex)
                return False
        log.debug("All sliders adjusted")

    # store all sim sliders as 'default' values
    def store_sim_sliders(self, sim_id: int, sims_configuration: dict, force_refresh: bool = False, auto_safe: bool = True):
        global oh, sim_default_values, modified_sims
        global preset_configuration_face_sliders_ids, preset_configuration_body_sliders_ids
        log.debug("store_sim_sliders(" + str(sim_id) + ", ...")
        try:
            if not oh:
                oh = O19Helper()
            o19sim: O19Sim = oh.get_sim_all(sim_id)
            if not o19sim.sim_info:
                log.debug(f"Can not access the sim (id={o19sim.sim_id}) right now, trying it again later")
                return
            appearance_attributes = PersistenceBlobs_pb2.BlobSimFacialCustomizationData()
            appearance_attributes.MergeFromString(o19sim.sim_info.facial_attributes)

            new_sim_sliders = {}
            # Add default values in case the slider is not found
            for slider_id in preset_configuration_face_sliders_ids:
                new_sim_sliders.update({slider_id: 0})
            for slider_id in preset_configuration_body_sliders_ids:
                new_sim_sliders.update({slider_id: 0})
            # Store the actual slider values in 'new_sim_sliders'
            for modifier in appearance_attributes.face_modifiers:
                if modifier.key in preset_configuration_face_sliders_ids:
                    new_sim_sliders.update({modifier.key: modifier.amount})
            for modifier in appearance_attributes.body_modifiers:
                if modifier.key in preset_configuration_body_sliders_ids:
                    new_sim_sliders.update({modifier.key: modifier.amount})

            # current_sim_slider = sims_configuration.get(sim_id)
            default_sim_slider = sim_default_values.get(sim_id)
            if force_refresh or default_sim_slider is None:
                # 1st call OR new: add the sim with current values
                sims_configuration.update({sim_id: new_sim_sliders})
                log.debug(f'__________________________________________Setting new default for slider {new_sim_sliders}')
            else:
                # Merge sliders, add only new slider values to the existing ones. Existing values will not be replaced.
                merged_sim_slider = {**new_sim_sliders, **default_sim_slider}
                sims_configuration.update({sim_id: merged_sim_slider})

            if auto_safe:
                self.save_config_file(sims_configuration)
            modified_sims.add(sim_id)
            sim_default_values = sims_configuration
        except Exception as ex:
            log.error("store_sim_sliders() Error occurred.", exception=ex)

    def save_config_file(self, sims_configuration, output=None):
        global oh, log_trace
        if log_trace:
            log.debug(f"save_config_file({sims_configuration})")
        else:
            log.info(f"save_config_file(sims_configuration)")
        try:
            if not oh:
                oh = O19Helper()
            current_directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            config_directory = os.path.join(current_directory, Oops19Constants.DIRECTORY_CONFIGURATION)
            file_name = os.path.join(config_directory, HighHeelsConstants.FILE_CONFIGURATION_CACHE)
            log.debug("Writing " + str(file_name))
            with open(file_name, 'wt') as fp:
                oh.print_pretty(fp, str(sims_configuration))
                fp.close()
        except Exception as ex:
            log.error("save_config_file() Error occurred.", exception=ex)

    def read_config_file(self, sims_configuration, output=None):
        global log_trace
        current_directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        config_directory = os.path.join(current_directory, Oops19Constants.DIRECTORY_CONFIGURATION)
        file_name = os.path.join(config_directory, HighHeelsConstants.FILE_CONFIGURATION_CACHE)
        if path.exists(file_name):
            log.debug("Reading '{file_name}'")
            with open(os.path.join(config_directory, file_name), 'rt') as fp:
                configuration_text = ""
                for line in fp:
                    configuration_text = configuration_text + line
                fp.close()
            try:
                _configuration = ast.literal_eval(configuration_text)
            except Exception as e:
                log.error("Could not read or parse file '{file_name}'", exception=e)
                return sims_configuration
        else:
            log.debug("Starting with empty file '{file_name}'.")
            _configuration = {}

        if log_trace:
            log.debug("Processing data: " + str(_configuration))
        global modified_sims
        modified_sims = set()
        for sim_id in _configuration:
            self.store_sim_sliders(sim_id, _configuration, force_refresh=False, auto_safe=False)

        if sims_configuration != _configuration:
            self.save_config_file(_configuration)
            sims_configuration = _configuration
        return sims_configuration

    def _read_configuration(self, config_directory=None, pattern_start: str = 'random.', pattern_end: str = '.ini'):
        global log_trace
        log.info(f"_read_configuration({config_directory}, {pattern_start}, {pattern_end})")
        _configuration = {}
        if config_directory and os.path.exists(config_directory):
            file_names = sorted(os.listdir(config_directory))
            if (len(file_names)) > 1:
                _default_ini = pattern_start + 'default' + '.ini'
                file_names.remove(_default_ini)
                file_names.append(_default_ini)
            for file_name in file_names:
                # read random.default.ini 1st. Insert 'x' temporarily to keep the list a list. list.remove() may change list to NoneType
                if file_name.startswith(pattern_start) and file_name.endswith(pattern_end):
                    log.info(f"Reading {file_name}")
                else:
                    if log_trace:
                        log.debug(f"Skipping {file_name}")
                    continue
                with open(os.path.join(config_directory, file_name), 'rt') as fp:
                    configuration_text = ""
                    for line in fp:
                        configuration_text = configuration_text + line
                    fp.close()
                    if log_trace:
                        log.debug(f"Configuration text: {configuration_text}")
                try:
                    cfg = ast.literal_eval(configuration_text)
                    _configuration = {**cfg, **_configuration}  # Merge dicts, keep existing values as is
                except Exception as e:
                    log.error("Could not read or parse file.", exception=e)
            if log_trace:
                log.debug(f"_get_configuration(): {_configuration}")
        return _configuration

    def read_ini_files(self) -> bool:
        log.info(f"read_ini_files()")
        global preset_configuration, preset_configuration_ids, preset_configuration_cas_ids
        global preset_configuration_blacklist_interaction_ids, preset_configuration_blacklist_sim_ids
        global preset_configuration_body_types, preset_configuration_modifier_ids
        global preset_configuration_face_sliders_ids, preset_configuration_body_sliders_ids
        global preset_body_type_2_face_sliders, preset_body_type_2_body_sliders

        global preset_id_2_face_sliders, preset_id_2_body_sliders
        global preset_cas_ids_2_id, preset_id_2_walkstypes
        global log_trace

        try:
            # Read all ini files to a temp variable before assigning it globally
            _preset_configuration = {}
            current_directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            config_directory = os.path.join(current_directory, Oops19Constants.DIRECTORY_CONFIGURATION)
            if not os.path.exists(config_directory):
                os.makedirs(config_directory)

            _slider_configuration = self._read_configuration(config_directory, 'slider.', '.ini')
            slider_lookup = dict()
            try:
                for package_name, sliders in _slider_configuration.items():
                    slider_lookup = {**sliders, **slider_lookup}
                log.debug(f"Sliders: {slider_lookup}")
            except Exception as e:
                log.error("Could not extract slider configuration.", exception=e)

            _preset_configuration = self._read_configuration(config_directory, 'preset.', '.ini')

            if os.path.exists(config_directory):
                # Add everything to sets and dicts for faster access.
                _configuration_ids = set()
                _configuration_cas_ids = set()
                _configuration_blacklist_interaction_ids = set()
                _configuration_blacklist_sim_ids = set()
                _configuration_body_types = set()

                _configuration_modifier_ids = set()
                _configuration_face_sliders_ids = set()
                _configuration_body_sliders_ids = set()
                _body_type_face_sliders = dict()
                _body_type_body_sliders = dict()

                _cas_ids_2_id = dict()
                _id_2_face_sliders = dict()
                _id_2_body_sliders = dict()
                _preset_id_2_walkstypes = dict()

                cas_item_lookup = {}
                for config_id, config_value in _preset_configuration.items():
                    if config_id < 0:
                        cas_item_lookup.update(config_value)
                        continue
                    _configuration_ids.add(config_id)
                    __x_cas_ids = config_value.get('CAS_IDs')
                    if not __x_cas_ids:
                        log.error(f"Field CAS_IDs missing for config_id {config_id}")
                        continue
                    for _name in __x_cas_ids:
                        __cas_ids = cas_item_lookup.get(_name)
                        if not __cas_ids:
                            log.error(f"CAS_IDs missing in config_id {config_id} for name {_name}")
                            continue
                        if log_trace:
                            log.debug(f"CAS_IDs: {_name}: {__cas_ids}")

                        _configuration_cas_ids.update(__cas_ids)
                        for __cas_id in __cas_ids:
                            _tmp_config_ids = _cas_ids_2_id.get(__cas_id, set())
                            _tmp_config_ids.add(config_id)
                            _cas_ids_2_id.update({__cas_id: _tmp_config_ids})  # update the configuration

                    __blacklist_interaction_ids = config_value.get(HighHeelsConstants.PRESET_CFG_BL_INTERACTION)
                    if __blacklist_interaction_ids is None:
                        _configuration_blacklist_interaction_ids = HighHeelsConstants.DEFAULT_BLACKLIST_INTERACTION_IDS  # []
                    else:
                        # [] is not none and will remove the default
                        _configuration_blacklist_interaction_ids = __blacklist_interaction_ids

                    __blacklist_sim_ids = config_value.get(HighHeelsConstants.PRESET_CFG_BL_SIM)
                    if __blacklist_sim_ids is None:
                        _configuration_blacklist_sim_ids = HighHeelsConstants.DEFAULT_BLACKLIST_SIM_IDS  # []
                    else:
                        # [] is not none and will remove the default
                        _configuration_blacklist_sim_ids = __blacklist_sim_ids

                    __body_type = config_value.get(HighHeelsConstants.PRESET_CFG_BODY_TYPE, HighHeelsConstants.DEFAULT_BODY_TYPE)
                    _configuration_body_types.add(__body_type)

                    __walkstyles = config_value.get(HighHeelsConstants.PRESET_CFG_WALKSTYLE, HighHeelsConstants.DEFAULT_WALKSTYLE)
                    _preset_id_2_walkstypes.update({config_id: __walkstyles})

                    __face_sliders = config_value.get(HighHeelsConstants.PRESET_CFG_FACE_MODIFIERS)  # may be empty or None
                    if __face_sliders:
                        _configuration_modifier_ids.add(HighHeelsConstants.BLOB_SIM_FACE_MODIFIER)
                        __slider_ids = set()
                        for slider_name, slider_value in __face_sliders.items():
                            slider_id = slider_lookup.get(slider_name)
                            if not slider_id:
                                log.error(f"Error: Slider_name {slider_name} missing in config_id {config_id}")
                                continue
                            __slider_ids.add(slider_id)
                            _configuration_face_sliders_ids.add(slider_id)

                            ___current_sliders = _id_2_face_sliders.get(config_id, dict())
                            ___current_sliders.update({slider_id: slider_value})
                            _id_2_face_sliders.update({config_id: ___current_sliders})  # update the configuration

                        ___current_sliders = _body_type_face_sliders.get(__body_type, set())
                        ___current_sliders.update(__slider_ids)
                        _body_type_face_sliders.update({__body_type: ___current_sliders})  # update the configuration

                    __body_sliders = config_value.get(HighHeelsConstants.PRESET_CFG_BODY_MODIFIERS)  # may be empty or None
                    if __body_sliders:
                        _configuration_modifier_ids.add(HighHeelsConstants.BLOB_SIM_BODY_MODIFIER)
                        __slider_ids = set()
                        for slider_name, slider_value in __body_sliders.items():
                            slider_id = slider_lookup.get(slider_name)
                            if not slider_id:
                                log.error(f"Error: Slider_name {slider_name} missing in config_id {config_id}")
                                continue
                            __slider_ids.add(slider_id)
                            _configuration_body_sliders_ids.add(slider_id)

                            ___current_sliders = _id_2_body_sliders.get(config_id, dict())
                            ___current_sliders.update({slider_id: slider_value})
                            _id_2_body_sliders.update({config_id: ___current_sliders})  # update the configuration

                        ___current_sliders = _body_type_body_sliders.get(__body_type, set())
                        ___current_sliders.update(__slider_ids)
                        _body_type_body_sliders.update({__body_type: ___current_sliders})  # update the configuration

                preset_configuration = _preset_configuration
                preset_configuration_ids = _configuration_ids
                preset_configuration_cas_ids = _configuration_cas_ids
                preset_configuration_blacklist_interaction_ids = _configuration_blacklist_interaction_ids
                preset_configuration_blacklist_sim_ids = _configuration_blacklist_sim_ids
                preset_configuration_body_types = _configuration_body_types
                preset_configuration_modifier_ids = _configuration_modifier_ids
                preset_configuration_face_sliders_ids = _configuration_face_sliders_ids
                preset_configuration_body_sliders_ids = _configuration_body_sliders_ids
                preset_body_type_2_face_sliders = _body_type_face_sliders
                preset_body_type_2_body_sliders = _body_type_body_sliders
                preset_cas_ids_2_id = _cas_ids_2_id
                preset_id_2_face_sliders = _id_2_face_sliders
                preset_id_2_body_sliders = _id_2_body_sliders
                preset_id_2_walkstypes = _preset_id_2_walkstypes

                # Config file parsed properly?
                if log_trace:
                    log.debug(f"preset_configuration_ids: {preset_configuration_ids}")
                    log.debug(f"preset_configuration_cas_ids: {preset_configuration_cas_ids}")
                    log.debug(f"preset_configuration_blacklist_interaction_ids: {preset_configuration_blacklist_interaction_ids}")
                    log.debug(f"preset_configuration_blacklist_sim_ids: {preset_configuration_blacklist_sim_ids}")
                    log.debug(f"preset_configuration_body_types: {preset_configuration_body_types}")
                    log.debug(f"preset_configuration_modifier_ids: {preset_configuration_modifier_ids}")
                    log.debug(f"preset_configuration_face_sliders_ids: {preset_configuration_face_sliders_ids}")
                    log.debug(f"preset_configuration_body_sliders_ids: {preset_configuration_body_sliders_ids}")
                    log.debug(f"preset_body_type_2_face_sliders: {preset_body_type_2_face_sliders}")
                    log.debug(f"preset_body_type_2_body_sliders: {preset_body_type_2_body_sliders}")
                    log.debug(f"preset_cas_ids_2_id: {preset_cas_ids_2_id}")
                    log.debug(f"preset_id_2_face_sliders: {preset_id_2_face_sliders}")
                    log.debug(f"preset_id_2_body_sliders: {preset_id_2_body_sliders}")
                    log.debug(f"preset_id_2_walkstypes: {preset_id_2_walkstypes}")

            else:
                log.error("Problem with configuration directory: '" + config_directory + "'")
        except Exception as ex:
            log.error("read_ini_files() Unknown error occurred.", exception=ex)
        return False


# DEBUG options
@sims4.commands.Command('o19.hh.trace', command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_trace(_connection=None):
    global log_trace
    output = sims4.commands.CheatOutput(_connection)
    try:
        log_trace = not log_trace
        output(f"debug_o19_hh_trace: {log_trace}")
    except Exception as ex:
        output("Error: " + str(ex))


# DEBUG options
@sims4.commands.Command('o19.hh.readini', command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_readini(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("debug_o19_hh_readini")
    try:
        main = HighHeels()
        main.read_ini_files()
        output("debug_o19_hh_readini: OK")
    except Exception as ex:
        output("Error: " + str(ex))


@sims4.commands.Command('o19.hh.config', command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_config(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("debug_o19_hh_config")
    try:
        global preset_configuration, preset_id_2_cas_ids, sim_default_values, preset_configuration_cas_ids
        output("preset_configuration: " + str(preset_configuration))
        time.sleep(1.5)
        output("preset_id_2_cas_ids: " + str(preset_id_2_cas_ids))
        time.sleep(1.5)
        output("sim_default_values: " + str(sim_default_values))
        time.sleep(1.5)
        output("preset_configuration_cas_ids: " + str(preset_configuration_cas_ids))
    except Exception as ex:
        output("Error: " + str(ex))


@sims4.commands.Command('o19.hh.loaded_again', command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_loaded_again(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("debug_o19_hh_loaded_again")
    try:
        # WARNING - will register the interceptor again and again. You have been warned.
        HighHeels()
        # Init.game_loaded()
        output("debug_o19_hh_loaded_again: OK")
    except Exception as ex:
        output("Error: " + str(ex))


