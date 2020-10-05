#
# LICENSE https://creativecommons.org/licenses/by-nc-nd/4.0/ https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#
# At 2021-01-01 the license shall be changed to https://creativecommons.org/licenses/by/4.0/
#

import os
from typing import Union, Tuple
import sims4.commands
import sims4
from buffs.appearance_modifier.appearance_modifier import AppearanceModifier
from high_heels.enums.constants import Oops19Constants
from high_heels.enums.hh_constants import HighHeelsConstants
from high_heels.modinfo import ModInfo

from high_heels.utilities.configuration import Configuration
from high_heels.utilities.helper_standalone import O19Helper, O19Sim

from protocolbuffers import PersistenceBlobs_pb2, Outfits_pb2, S4Common_pb2
from sims.outfits.outfit_enums import OutfitCategory, OutfitFilterFlag

from sims.outfits.outfit_tracker import OutfitTrackerMixin


# Default after startup: dump sliders
do_dump_sliders = True

# Default after startup: dump outfit
do_dump_outfit = True

class DumpData:
    def __init__(self, output=None):
        self.output = output
        try:
            self.oh = O19Helper(output=output)
            try:
                self.current_directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
                self.dump_directory = os.path.join(self.current_directory, Oops19Constants.DIRECTORY_DUMP)
                if not os.path.exists(self.dump_directory):
                    os.makedirs(self.dump_directory)
                self.ini_directory = os.path.join(self.current_directory, Oops19Constants.DIRECTORY_INI)
                _outfit_ini_file = os.path.join(self.ini_directory, HighHeelsConstants.FILE_INI_BODY_TYPES)
                _outfit_conf: Configuration = Configuration(ModInfo.get_identity(), _outfit_ini_file, load_configuration=True, auto_save=False, backup_id='')
                _o_c, _ = _outfit_conf.get_configuration()
                self.outfit_descriptions: dict = _o_c

                _sliders_ini_file = os.path.join(self.ini_directory, HighHeelsConstants.FILE_INI_SLIDERS)
                _sliders_conf: Configuration = Configuration(ModInfo.get_identity(), _sliders_ini_file, load_configuration=True, auto_save=False, backup_id='')
                _s_c, _ = _outfit_conf.get_configuration()
                self.slider_descriptions: dict = _s_c
            except Exception as e:
                self.oh.log("DumpData.__init__() Error.", e)
        except Exception as ex:
            if (output):
                output(f"DumpData.__init__() - Error: {ex}")

    def dump_sim_data(self, p_sim = None, dump_all: bool = False):
        global do_dump_sliders, do_dump_outfit
        oh = self.oh
        o19sim: O19Sim = oh.get_sim_all(p_sim)
        if not o19sim.sim_info:
            oh.log(f"DumpData.dump_sim_data({p_sim}, {dump_all}) Sim not initialized properly.")
            return
        oh.log(f"DumpData.dump_sim_data({p_sim}, {dump_all})")

        outfit_category_and_index: Tuple[OutfitCategory, int] = o19sim.sim_info.get_current_outfit()
        outfit_category: OutfitCategory = outfit_category_and_index[0]
        outfit_index: int = outfit_category_and_index[1]
        if isinstance(outfit_category, int):
            outfit_category = OutfitCategory(outfit_category)
        oh.log(f"Dumping Sim sim_id={o19sim.sim_id} sim_name={o19sim.sim_name} {outfit_category.name}[{outfit_index}]")

        # DUMP sliders for current (=all) outfit
        if do_dump_sliders:
            self.dump_sliders(o19sim, outfit_category, outfit_index)

        # DUMP single outfit
        # outfit_descriptions: dict = get_configuration(current_directory, HighHeelsConstants.FILE_INI_BODY_TYPES)
        if do_dump_outfit and not dump_all:
            self.dump_outfit(o19sim, outfit_category, outfit_index)

        # DUMP all outfits
        if dump_all:
            for outfit_category in OutfitCategory: # == range(-1, 12):
                if outfit_category == OutfitCategory.CURRENT_OUTFIT:
                    # Do not log the current (-1) OutfitCategory as it is the same as one of the following OutfitCategory
                    continue
                for outfit_index in range(o19sim.sim_info.get_number_of_outfits_in_category(outfit_category)): #  == range(5):
                    oh.log(outfit_index)
                    self.dump_outfit(o19sim, outfit_category, outfit_index)

    def dump_sliders(self, o19sim: O19Sim, outfit_category:int = 0, outfit_index:int = 0):
        oh = self.oh
        try:
            if isinstance(outfit_category, int):
                outfit_category = OutfitCategory(outfit_category)
            appearance_attributes = PersistenceBlobs_pb2.BlobSimFacialCustomizationData()
            appearance_attributes.MergeFromString(o19sim.sim_info.facial_attributes)

            _sculpts = {}
            for modifier in appearance_attributes.sculpts:
                _sculpts.update({modifier: None})

            _face_modifiers = {}
            for modifier in appearance_attributes.face_modifiers:
                _slider_description = self.slider_descriptions.get(modifier.key)
                _face_modifiers.update({modifier.key: {_slider_description: modifier.amount}})

            _body_modifiers = {}
            for modifier in appearance_attributes.body_modifiers:
                _slider_description = self.slider_descriptions.get(modifier.key)
                _body_modifiers.update({modifier.key: {_slider_description: modifier.amount}})

            slider_configuration = {
                o19sim.sim_id: {
                    HighHeelsConstants.OUTPUT_SIM_NAME: o19sim.sim_name,
                    HighHeelsConstants.BLOB_SIM_BODY_MODIFIER: _body_modifiers,
                    HighHeelsConstants.BLOB_SIM_FACE_MODIFIER: _face_modifiers,
                    HighHeelsConstants.BLOB_SIM_SCULPTS: _sculpts,
                }
            }

            # add the current outfit_category and index to the file name
            # The content is always the same unless the sliders were modified in CAS
            slider_filename = os.path.join(self.dump_directory, HighHeelsConstants.FILE_DUMP_SLIDER.format(f"{o19sim.sim_id}.{o19sim.sim_filename}.{outfit_category}.{outfit_index}"))
            with open(slider_filename, 'wt') as fp:
                oh.print_pretty(fp, str(slider_configuration))
                fp.close()
        except Exception as e:
            oh.log("DumpData.dump_sliders() - Error processing sliders.", e)

    def dump_outfit(self, o19sim: O19Sim, outfit_category: OutfitCategory = OutfitCategory(OutfitCategory.EVERYDAY), outfit_index:int = 0):
        oh = self.oh

        if isinstance(outfit_category, int):
            outfit_category = OutfitCategory(outfit_category)
        outfit = o19sim.sim_info.get_outfit(outfit_category, outfit_index)
        try:
            num_clothing_items = len(outfit.body_types)
            _body_types_and_part_ids = {}
            for idx in range(num_clothing_items):
                _body_type_description = self.outfit_descriptions.get(outfit.body_types[idx])
                _body_types_and_part_ids.update({outfit.body_types[idx]: {_body_type_description: outfit.part_ids[idx]}})

            outfit_configuration = {
                HighHeelsConstants.OUTPUT_SIM_ID: o19sim.sim_id,
                HighHeelsConstants.OUTPUT_SIM_NAME: o19sim.sim_name,
                HighHeelsConstants.OUTPUT_SIM_OUTFIT_CATEGORY_TEXT: outfit_category.name,
                HighHeelsConstants.OUTPUT_SIM_OUTFIT_CATEGORY: outfit_category.value,
                HighHeelsConstants.OUTPUT_SIM_OUTFIT_INDEX: outfit_index,
                HighHeelsConstants.OUTPUT_OUTFIT: _body_types_and_part_ids
            }

            # add the current outfit_category and index to the file name
            outfit_filename = os.path.join(self.dump_directory, HighHeelsConstants.FILE_DUMP_OUTFIT.format(f"{o19sim.sim_id}.{o19sim.sim_filename}.{outfit_category}.{outfit_index}"))
            with open(outfit_filename, 'wt') as fp:
                oh.print_pretty(fp, str(outfit_configuration))
                fp.close()
        except Exception as ex:
            oh.log("DumpData.dump_outfit() - Error processing outfit.", ex)


class Res:
    O19_HH_DUMP__HELP = 'o19.dump'
    O19_HH_DUMP_OUTFIT__TOGGLE = O19_HH_DUMP__HELP + ".outfit"
    O19_HH_DUMP_SLIDER__TOGGLE = O19_HH_DUMP__HELP + ".slider"
    O19_HH_DUMP_SIM = O19_HH_DUMP__HELP + ".sim"
    O19_HH_DUMP_ALL = O19_HH_DUMP__HELP + ".all"
    O19_HH_DUMP_CHANGE = O19_HH_DUMP__HELP + ".outfit"
    O19_HH_DUMP_PART = O19_HH_DUMP__HELP + ".part"

    O19_HH_DUMP_HELP = {
        O19_HH_DUMP__HELP: ': Show this help message',
        O19_HH_DUMP_OUTFIT__TOGGLE: ': Toggle writing of outfits to file',
        O19_HH_DUMP_SLIDER__TOGGLE: ': Toggle writing of sliders to file',
        O19_HH_DUMP_SIM: f' [sim]: Dump current outfit and sliders (may be disabled with {O19_HH_DUMP_OUTFIT__TOGGLE} and {O19_HH_DUMP_SLIDER__TOGGLE})',
        O19_HH_DUMP_ALL: ' [sim]: Dump all outfits of the sim.',
        O19_HH_DUMP_CHANGE: ' [cat] [idx] [sim]: Set the outfit, "cat" and "idx" are required.',
        O19_HH_DUMP_PART: ' [body_type] [cas_part] [sim]: Show/Hide outfit part.',
        '[cat]': ': A number [0-11] or a text string. Default is 0 (EVERYDAY)',
        '[idx]': ': A number [0-4] to specify the outfit index. The outfit should exist. Default is 0.',
        '[sim]': ': If the parameter is missing the current sim will be processed. Otherwise the sim_id or the name in the format "Mary Kate#Smith" (for "Mary Kate" (first names) "Smith" (last name)) can be specified. Also "M#S" may work.',
    }
    DELETE_ME_OUTFIT_CAT_ABBR = {
        'e': 'EVERYDAY', 'f': 'FORMAL', 'a': 'ATHLETIC', 's': 'SLEEP',
        'p': 'PARTY', 'i': 'BATHING', 'c': 'CAREER', 'si': 'SITUATION',
        'sp': 'SPECIAL', 'sw': 'SWIMWEAR', 'hw': 'HOTWEATHER', 'cw': 'COLDWEATHER'
    }
    OUTFIT_CAT_NR = {
        '0': 'EVERYDAY', '1': 'FORMAL', '2': 'ATHLETIC', '3': 'SLEEP',
        '4': 'PARTY', '5': 'BATHING', '6': 'CAREER', '7': 'SITUATION',
        '8': 'SPECIAL', '9': 'SWIMWEAR', '10': 'HOTWEATHER', '11': 'COLDWEATHER'
    }


@sims4.commands.Command(Res.O19_HH_DUMP__HELP, command_type=sims4.commands.CommandType.Live)
def o19_hh_dump_help(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        oh = O19Helper(output=output)
        for key, value in Res.O19_HH_DUMP_HELP.items():
            output(f"{key}{value}")
        oh.write_to_console(output, header="[cat] numbers ('e' or 'ev' for EVERYDAY supported):", values=Res.OUTFIT_CAT_NR)
    except Exception as ex:
        output(f"{Res.O19_HH_DUMP__HELP} - Error: {ex}")


@sims4.commands.Command(Res.O19_HH_DUMP_OUTFIT__TOGGLE, command_type=sims4.commands.CommandType.Live)
def o19_hh_dump_toggle_outfit(_connection=None):
    global do_dump_outfit
    output = sims4.commands.CheatOutput(_connection)
    try:
        do_dump_outfit = not do_dump_outfit
        output(f"{Res.O19_HH_DUMP_OUTFIT__TOGGLE} - Logging of outfits: {do_dump_outfit}")
    except Exception as ex:
        output(f"{Res.O19_HH_DUMP_OUTFIT__TOGGLE} - Error: {ex}")


@sims4.commands.Command(Res.O19_HH_DUMP_SLIDER__TOGGLE, command_type=sims4.commands.CommandType.Live)
def o19_hh_dump_slider(_connection=None):
    global do_dump_sliders
    output = sims4.commands.CheatOutput(_connection)
    try:
        do_dump_sliders = not do_dump_sliders
        output(f"{Res.O19_HH_DUMP_SLIDER__TOGGLE} - Logging of sliders: {do_dump_sliders}")
    except Exception as ex:
        output(f"{Res.O19_HH_DUMP_SLIDER__TOGGLE} - Error: {ex}")

@sims4.commands.Command(Res.O19_HH_DUMP_SIM, command_type=sims4.commands.CommandType.Live)
def debug_hh_dump_sim(p_sim = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        dd = DumpData(output)
        output(f"{Res.O19_HH_DUMP_SIM} ({p_sim})")
        dd.dump_sim_data(p_sim, dump_all=False)
        output(f"{Res.O19_HH_DUMP_SIM} (OK)")
    except Exception as ex:
        output(f"{Res.O19_HH_DUMP_SIM} - Error: {ex}")


@sims4.commands.Command(Res.O19_HH_DUMP_ALL, command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_dump_all(p_sim = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        dd = DumpData(output)
        output(f"{Res.O19_HH_DUMP_ALL} ({p_sim})")
        dd.dump_sim_data(p_sim, dump_all=True)
        output(f"{Res.O19_HH_DUMP_ALL} (OK)")
    except Exception as ex:
        output(f"{Res.O19_HH_DUMP_ALL} - Error: {ex}")

@sims4.commands.Command(Res.O19_HH_DUMP_CHANGE, command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_dump_all(p_outfit_category: str = '0', p_outfit_index: str = '0', p_sim = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        oh = O19Helper(output=output)
        try:
            outfit_category_num: int = int(p_outfit_category)
            # tbd: check range
            outfit_category: OutfitCategory = OutfitCategory(outfit_category_num)
        except Exception as e:
            # not a number, expand the string value and use it
            outfit_category_str: str = oh.expand_string(p_outfit_category, Res.OUTFIT_CAT_NR)
            # tbd: check range
            outfit_category: OutfitCategory = OutfitCategory[outfit_category_str]
        outfit_index = int(p_outfit_index)
        outfit_category_and_index: Tuple[OutfitCategory, int] = (outfit_category, outfit_index)
        output(f"{Res.O19_HH_DUMP_CHANGE} - Trying to set outfit {outfit_category_and_index}")
        o19sim: O19Sim = oh.get_sim_all(p_sim)
        OutfitTrackerMixin.try_set_current_outfit(o19sim.sim_info, outfit_category_and_index, do_spin=False, arb=None, interaction=None)
        output(f"{Res.O19_HH_DUMP_CHANGE} - OK")
    except Exception as ex:
        output(f"{Res.O19_HH_DUMP_ALL} - Error: {ex}")

@sims4.commands.Command(Res.O19_HH_DUMP_PART, command_type=sims4.commands.CommandType.Live)
def debug_o19_hh_part_toggle(p_body_part = None, p_cas_part = None, p_sim = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    try:
        output("A")
        body_part = int(p_body_part)
        cas_part = int(p_cas_part)
        oh = O19Helper(output=output)
        o19sim: O19Sim = oh.get_sim_all(p_sim)

        outfit_category_and_index: Tuple[OutfitCategory, int] = o19sim.sim_info.get_current_outfit()
        outfit_category: OutfitCategory = outfit_category_and_index[0]
        outfit_index: int = outfit_category_and_index[1]
        outfit = o19sim.sim_info.get_outfit(outfit_category, outfit_index)
        #outfit = o19sim.sim_info.get_outfit(-1, 0)

        num_body_types = len(outfit.body_types)
        _body_types_and_part_ids = {}

        try:
            output(f"  {outfit.body_types}  --------")
            for idx in range(num_body_types):
                if body_part == outfit.body_types[idx]:
                    break
            # idx = (i for i, x in enumerate(outfit.body_types) if x == body_part)
            output(f"{idx}  {outfit.body_types[idx]} {type(outfit.body_types)}")

            outfit.body_types.remove(body_part)
            del outfit.body_types[idx]
            output(f"{idx} {outfit.body_types[idx]}")

            cas_part_id = outfit.part_ids[idx]
            outfit.part_ids.remove(cas_part_id)
            output(f"  {outfit.body_types}  --------")

        except Exception as e:
            output(f"XX {e}")

        for idx in range(num_body_types):
            output(f"{idx} {outfit.body_types[idx]}")
            output(f"  {outfit.body_types}")
            if body_part == outfit.body_types[idx]:
                cas_part_id = outfit.part_ids[idx]
                # output(f"{outfit.part_ids[idx]}")
                try:

                    outfit.body_types_list.body_types.remove(idx)
                    #outfit.body_types.remove(body_part)
                except:
                    output("body_types err")
                    pass
                try:
                    outfit.parts.ids.remove(idx)
                    #outfit.part_ids.remove(cas_part_id)
                except:
                    output("part_ids err")
                    pass
                #del outfit.body_types[idx]
                #del outfit.part_ids[idx]
                output("DEL")
                break
        # o19sim.sim_info._base.outfit_type_and_index = outfit_category_and_index
        # OutfitTrackerMixin.try_set_current_outfit(o19sim.sim_info, outfit_category_and_index, do_spin=False, arb=None, interaction=None)
        rv = o19sim.sim_info.generate_outfit(outfit_category=outfit_category, outfit_index=outfit_index, filter_flag=OutfitFilterFlag.NONE)
        outfit_msg = o19sim.sim_info.save_outfits()
        output(f"outfit_msg: {type(outfit_msg)} = {outfit_msg}")
        for outfit in outfit_msg.outfits:
            output(f"outfit: {type(outfit)} = {outfit}")
            outfit_id = outfit.outfit_id  #
            category = outfit.category
            outfit.parts = S4Common_pb2.IdList()
            parts = outfit.parts
            body_types_list = outfit.body_types_list = Outfits_pb2.BodyTypesList()

            match_hair_style = outfit.match_hair_style
            outfit_flags = outfit.outfit_flags
            outfit_flags_high = outfit.outfit_flags_high
            output(f"outfit_id: {type(outfit_id)} = {outfit_id}; category: {type(category)} = {category}; parts: {type(parts)} = {parts}")
            output(f"body_types_list: {type(body_types_list)} = {body_types_list}; match_hair_style: {type(match_hair_style)} = {match_hair_style}; outfit_flags: {type(outfit_flags)} = {outfit_flags}; outfit_flags_high: {type(outfit_flags_high)} = {outfit_flags_high}")

        output(f"{outfit_msg}")

        appearance_attributes = PersistenceBlobs_pb2.BlobSimFacialCustomizationData()

        #outfit = o19sim.sim_info.get_outfit(outfit_category, outfit_index)
        #outfit = o19sim.sim_info.get_outfit_data()
        #outfit.part_ids = []
        #outfit.body_types = []
        #outfit.body_types.append(26)
        #outfit.part_ids.append(16249576789170727729)
#
#        o19sim.sim_info.resend_outfits()
#        #o19sim.sim_info.set_current_outfit(outfit)

        # o19sim.sim_info.resend_physical_attributes()
        output("Z")
    except Exception as ex:
        output(f"{Res.O19_HH_DUMP_PART} - Error: {ex}")

def dddd(output = None, p_sim = None, cas_part  = None):
    guid = 10933481383020127886 # fnv(text='Oops19', n=64, ascii_2_lower=False, utf16=True, set_high_bit=False)
    src = None # src= self
    oh = O19Helper(output=output)
    o19sim: O19Sim = oh.get_sim_all(p_sim)
    appearance_tracker = o19sim.sim_info.appearance_tracker
    appearance_tracker.remove_appearance_modifiers(guid, source=src)
    modifiers = []
    # Getting all CAS parts and setting shoud_toggle to True should remove all CAS parts.
    # cas_part(int): The cas part
    # should_toggle(bool): True: Set or remove it. - False: Set the part, do not remove it.
    # replace_with_random(bool): True: Replace CAS part with a random variant
    # update_genetics(bool): True: Permanent modification
    # _is_combinable_with_same_type(bool): ?
    # remove_conflicting(bool): True: Conflicting parts are removed from the outfit.
    # outfit_type_compatibility(?): ?
    # expect_invalid_parts(bool): True: Raise no exception for invalid parts
    modifier = AppearanceModifier.SetCASPart(cas_part=cas_part, should_toggle=True, replace_with_random=False, update_genetics=False, _is_combinable_with_same_type=True, remove_conflicting=False, outfit_type_compatibility=None)
    modifiers.append(modifier)
    for modifier in modifiers:
        appearance_tracker.add_appearance_modifier(modifier, guid, 1, False, source=src)
    appearance_tracker.evaluate_appearance_modifiers()
    o19sim.sim_info.resend_outfits()
    #o19sim.sim_info.resend_physical_attributes()


