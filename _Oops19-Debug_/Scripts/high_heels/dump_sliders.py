#
# LICENSE https://creativecommons.org/licenses/by-nc-nd/4.0/ https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#
# At 2021-01-01 the license shall be changed to https://creativecommons.org/licenses/by/4.0/
#

from typing import Union, Any

import services
import sims4.commands
import sims4
from high_heels.enums.hh_constants import HighHeelsConstants
from high_heels.utilities.helper_standalone import O19Helper, O19Sim
from protocolbuffers import PersistenceBlobs_pb2
from protocolbuffers.PersistenceBlobs_pb2 import BlobSimFacialCustomizationData
from sims.sim_info import SimInfo

oh = None
ms = None
global_config = {}
global_o19sim = None
global_slider_key = -1
global_modifier_type = -1

# To use this class we need to dump the SIM and all sliders.
# 1. To modify the active sim use 'o19.slider.set_sim'
#     To modify a random sim read 'debug/sliders.123.0.0.Ting#Tong.txt'
#     The 2nd line is the sim_id, it is also in the file name. Set it with 'o19.slider.set_sim 123'
#     And if this is not yet enough you can set it with 'o19.slider.set_sim "all first names#all last names"'. Do not replace ' ' with '_'.
# 2. Choose a body or face slider and the id. In 'debug/sliders.123.0.0.Ting#Tong.txt' '2:' are body sliders while '1:' are face sliders.
#     Set it with 'o19.slider.set_slider 987 ' (or 1 for face)
# 3. To set the slider to a specific value betwwen 0 and 1 use 'o19.slider.to 0.123'
#
# You can modify the sim ot the sliders at any time. I'm not responsible for ugly sims with all sliders set to 0
#
# 3b. To set the slider to min or max use 'o19.slider.toggle' - it helps to identify sliders
#     To restore the previous slider value use 'o19.slider.toggle off' (or 'x')
#     WARNING: The restore values are stored in memory, if you go to CAS to travel with the sim they are lost.
#
# 4. To show the stored in-memory values use 'o19.slider.cfg'.
#     The output will be like this: { sim_id.1: { slider_id.1: { modifier_type: slider_value }, slider_id.2: { modifier_type: slider_value }, }, sim_id.2 { ... }}

class ModifySliders:
    def __init__(self, output=None):
        self.output = output
        try:
            self.oh = O19Helper(output=output)
        except Exception as ex:
            if (output):
                output(f"ModifySliders.__init__() - Error: {ex}")

    def slide_to(self, sim_info: SimInfo = None, modifier_type: int = -1, slider_id: int = -1, slider_value: Union[float, None] = None) -> Union[bool, float]:
        """

        :param sim_info:
        :param modifier_type:
        :param slider_id:
        :param slider_value:
        :return:
            float[0..1]: Previous value of the existing modifier which was modified.
            True: New slider was added and value applied.
            False: Slider does not exist and no new value was given.
            float[-1]: Invalid parameters error
            float[-2]: Error processing the request
        """
        #global do_dump_sliders, do_dump_outfit
        oh = self.oh
        oh.log(f"slide_to(SimInfo, {modifier_type}, {slider_id}, {slider_value})")
        if (SimInfo is None) or (modifier_type < HighHeelsConstants.BLOB_SIM_FACE_MODIFIER) or (modifier_type > HighHeelsConstants.BLOB_SIM_BODY_MODIFIER) or (slider_id < 0):
            oh.log(f"slide_to() error: Invalid parameters.")
            return -1.0
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
                    oh.log(f"slide_to() Modifier found")
                    found_modifier = True
                    break

            if not found_modifier:
                if slider_value is None:
                    return False  # Modifier not found and no new value specified
                # Add slider (hopefully it exits in-game)
                oh.log(f"slide_to() Modifier not found ... adding it on-the-fly")
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
            oh.log(f"slide_to() Error", ex)
        return -2.0



def slide_to_v1(p_sim_id: Union[int, str], p_slider_key: Union[int, str], p_slider_value: Union[str, None], p_modifier_type: Union[int, str], output) -> Union[bool, float]:
    # rv == False .... Slider not found and not modified (p_slider_value = None)
    # rv == True ..... Slider not found, added and set to p_slider_value
    # rv == [0..1] ... Slider found, rv is the previous setting. Set to p_slider_value unless None
    try:
        output("slide_to " + str(p_sim_id) + " " + str(p_slider_key) + " " + str(p_slider_value) + " " + str(p_modifier_type))
        if p_sim_id is None:
            client = services.client_manager().get_first_client()
            sim_info: SimInfo = client.active_sim_info
            sim_id: int = sim_info.id
        else:
            sim_id: int = int(p_sim_id)
            sim_info: SimInfo = services.sim_info_manager().get(sim_id)

        slider_key = int(p_slider_key)
        modifier_type = int(p_modifier_type)
        if p_slider_value is not None: # Check for None. '0' is not None. But 'if 0' == 'if None'.
            slider_value = float(p_slider_value)
        else:
            slider_value = None


        appearance_attributes = PersistenceBlobs_pb2.BlobSimFacialCustomizationData()
        appearance_attributes.MergeFromString(sim_info.facial_attributes)

        found_modifier = False
        if modifier_type == 2:  # BLOB_SIM_BODY_MODIFIER = 2    # BLOB_SIM_FACE_MODIFIER = 1
            for modifier in appearance_attributes.body_modifiers:
                if modifier.key == slider_key:
                    found_modifier = True
                    output("body_modifier found")
                    break
            if not found_modifier:
                if not slider_value:
                    return False  # Slider not found and no new value specified
                # Add slider (hopefully it exits in-game)
                modifier = BlobSimFacialCustomizationData.Modifier()
                modifier.key = slider_key  # set key & value
                modifier.amount = slider_value
                appearance_attributes.body_modifiers.append(modifier)

                sim_info.facial_attributes = appearance_attributes.SerializeToString()
                sim_info.resend_facial_attributes()
                return True  # Slider added

        elif modifier_type == 1:  # BLOB_SIM_FACE_MODIFIER = 1
            for modifier in appearance_attributes.face_modifiers:
                if modifier.key == slider_key:
                    found_modifier = True
                    output("face_modifier found")
                    break
            if not found_modifier:
                if not slider_value:
                    return False  # Slider not found and no new value specified
                # Add slider (hopefully it exits in-game)
                modifier = BlobSimFacialCustomizationData.Modifier()
                modifier.key = slider_key  # set key & value
                modifier.amount = slider_value
                appearance_attributes.face_modifiers.append(modifier)

                sim_info.facial_attributes = appearance_attributes.SerializeToString()
                sim_info.resend_facial_attributes()
                return True  # Slider added

        current_value = modifier.amount
        if slider_value is not None: # Check for None. '0' is not None. But 'if 0' == 'if None'.
            modifier.amount = slider_value

            sim_info.facial_attributes = appearance_attributes.SerializeToString()
            sim_info.resend_facial_attributes()

        return current_value

    except Exception as ex:
        output("Error: " + str(ex))
    return -1


@sims4.commands.Command('o19.slider.cfg', command_type=sims4.commands.CommandType.Live)
def debug_o19_slider_to(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    global global_config
    output("o19.slider.cfg: " + str(global_config
                                    ))

class Res:
    O19_HH_SLIDERS_HELP = 'o19.slider'
    O19_HH_SLIDERS_SIM = O19_HH_SLIDERS_HELP + ".sim"
    O19_HH_SLIDERS_TO = O19_HH_SLIDERS_HELP + ".to"
    O19_HH_SLIDERS_TOGGLE = O19_HH_SLIDERS_HELP + ".toggle"
    O19_HH_SLIDERS_CFG = O19_HH_SLIDERS_HELP + ".cfg"
    O19_HH_SLIDERS_MIN = O19_HH_SLIDERS_HELP + ".min"
    O19_HH_SLIDERS_MAX = O19_HH_SLIDERS_HELP + ".max"

    O19_HH_SLIDERS_HELP_TEXT = {
        O19_HH_SLIDERS_HELP: ': Show this help message',
        O19_HH_SLIDERS_SIM: ' [sim]: Set the sim for all further slider modifications. It will be stored in-memory for further reference.',
        O19_HH_SLIDERS_TO: ' [mod] [slider] [value]: Set the slider to a new value (if value specified). If no sim was set before ".sim" will be called internally. All values will be stored in-memory for further reference.',
        O19_HH_SLIDERS_TOGGLE: ' [off]: Toggle the current slider and set it to 0 or 1. Add a parameter to restore the previous value. The slider has to be set beforehand with ".to".',
        O19_HH_SLIDERS_CFG: ' : Print the in-memory values to console.',
        # O19_HH_SLIDERS_MIN: '[mod] [n]: Set "n" sliders to 0. The first slider found which is not 0 will be set to 0',
        # O19_HH_SLIDERS_MAX: '[mod] [n]: Set "n" sliders to 1.',
        '[sim]': ': If the parameter is missing the current sim will be processed. Otherwise the sim_id or the name in the format "Mary Kate#Smith" (for "Mary Kate" (first names) "Smith" (last name)) can be specified. Also "M#S" may work.',
        '[mod]': ' Face (1) or Body (2) modifier for this slider. Usually 2 unless you want to do plastic face surgery (required).',
        '[slider]': 'The slider ID to modify.',
        # '[slider]': 'The slider ID to modify. Expansion (160 for 18064054205832047496) is supported for named all sliders in ini/sliders.ini (required).',
        '[value]': ': The new float slider value [0..1]. If missing the current slider value will be read and printed.',
    }


@sims4.commands.Command(Res.O19_HH_SLIDERS_HELP, command_type=sims4.commands.CommandType.Live)
def o19_hh_sliders_help(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        for key, value in Res.O19_HH_SLIDERS_HELP_TEXT.items():
            output(key + value)
    except Exception as ex:
        output(f"{Res.O19_HH_SLIDERS_HELP}() Error: " + str(ex))

@sims4.commands.Command(Res.O19_HH_SLIDERS_SIM, command_type=sims4.commands.CommandType.Live)
def o19_hh_sliders_sim(p_sim = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    global oh, global_o19sim
    try:
        output(f"{Res.O19_HH_SLIDERS_SIM}({p_sim})")
        if not oh:
            oh = O19Helper(output)
        o19sim: O19Sim = oh.get_sim_all(p_sim, output)
        if not o19sim.sim_info:
            output("Error: Sim not found.")
            return
        output(f"Selected sim: {o19sim.sim_name} ({o19sim.sim_id})")
        global_o19sim = o19sim
    except Exception as ex:
        output(f"{Res.O19_HH_SLIDERS_SIM}() Error: " + str(ex))


@sims4.commands.Command(Res.O19_HH_SLIDERS_TO, command_type=sims4.commands.CommandType.Live)
def o19_hh_sliders_to(p_modifier_type=None, p_slider_key=None, p_slider_value=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    global oh, ms, global_config, global_o19sim, global_modifier_type, global_slider_key
    try:
        output(f"{Res.O19_HH_SLIDERS_TO}({p_modifier_type}, {p_slider_key}, {p_slider_value})")
        if (p_modifier_type is None) or (p_slider_key is None):
            output("Error: 'mod' and 'slider' are required parameters.")
            return
        modifier_type = int(p_modifier_type)
        slider_key = int(p_slider_key)
        if p_slider_value:
            slide_to_value = float(p_slider_value)
        else:
            slide_to_value = None
        if (modifier_type < 1)  or (modifier_type > 2) or (slider_key < 0) or (slide_to_value < 0) or (slide_to_value > 1):
            output("Error: Parameters out of range.")
            return
        # TODO expand slider_key

        if not global_o19sim:
            o19_hh_sliders_sim(_connection)
        if not global_o19sim:
            output("Error: Active sim could not be set as global sim.")
            return

        try:
            globally_stored_slider_value = global_config.get(global_o19sim).get(modifier_type).get(slider_key)
        except:
            # Could not get the value, likely not initialized
            globally_stored_slider_value = None

        if not ms:
            ms = ModifySliders(output)
        # Slide to new value
        previous_slider_value = ms.slide_to(global_o19sim.sim_info, modifier_type, slider_key, slide_to_value)
        if (previous_slider_value is False) or (previous_slider_value < 0):
            output("Error setting slider value.")
            return
        if globally_stored_slider_value is None:
            # add sim, slider_key and _value to global configuration
            if previous_slider_value is True:
                # Slider was added, use 0.0 as default value
                previous_slider_value = 0.0
            global_config.update({global_o19sim: {modifier_type: {slider_key: previous_slider_value}}})
            globally_stored_slider_value = previous_slider_value

        output(f"{Res.O19_HH_SLIDERS_TO}() Slider adjusted (default / previous values: {globally_stored_slider_value} / {previous_slider_value})")
        global_modifier_type = modifier_type
        global_slider_key = slider_key
    except Exception as ex:
        output("Error: " + str(ex))


@sims4.commands.Command(Res.O19_HH_SLIDERS_TOGGLE, command_type=sims4.commands.CommandType.Live)
def o19_hh_sliders_toggle(end_toggle: Union[None, str] = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    global oh, ms, global_config, global_o19sim, global_modifier_type, global_slider_key
    try:
        output(f"{Res.O19_HH_SLIDERS_TO}(end_toggle={end_toggle})")
        if global_slider_key == -1:
            output("Error: Initialize 'mod' and 'slider' first.")
            return

        if not global_o19sim:
            o19_hh_sliders_sim(_connection)
        if not global_o19sim:
            output("Error: Active sim could not be set as global sim.")
            return

        if not ms:
            ms = ModifySliders(output)

        try:
            globally_stored_slider_value = global_config.get(global_o19sim).get(global_modifier_type).get(global_slider_key)
        except:
            # Could not get the value, likely not initialized
            globally_stored_slider_value = None

        if end_toggle:
            if globally_stored_slider_value is not None:
                ms.slide_to(global_o19sim.sim_info, global_modifier_type, global_slider_key, globally_stored_slider_value)
            else:
                output("Error: No default value found.")
        else:
            current_slider_value = ms.slide_to(global_o19sim.sim_info, global_modifier_type, global_slider_key, None)
            if current_slider_value < 0.5:
                new_slider_value: str = "1"
            else:
                new_slider_value: str = "0"
            if globally_stored_slider_value is None:
                # Call console method to make sure that the default value gets saved
                o19_hh_sliders_to(global_modifier_type, global_slider_key, new_slider_value, _connection)
            else:
                # Direct slide_to() call
                ms.slide_to(global_o19sim.sim_info, global_modifier_type, global_slider_key, new_slider_value)
    except Exception as ex:
        output("Error: " + str(ex))
