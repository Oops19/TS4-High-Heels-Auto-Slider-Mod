#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#


import os
import time
from weakref import WeakKeyDictionary

import routing
import sims4.commands
import sims4.hash_util
import sims4.resources
import sims4.resources
from high_heels.enums.constants import Oops19Constants
from high_heels.utilities.helper_standalone import O19Helper, O19Sim
from routing.walkstyle.walkstyle_enums import WalkStylePriority
from routing.walkstyle.walkstyle_request import WalkStyleRequest
from routing.walkstyle.walkstyle_tuning import Walkstyle
from sims4.math import MAX_INT32

_walk_style_requests = WeakKeyDictionary()

# fetch the walkstyles one time and keep them for fast lookups
styles = {}

# Oops19 Helper class
oh = None
class DumpWalkstyle:
    pass

class Res:
    O19_WALK__HELP = 'o19.walk'
    O19_WALK_LIST = O19_WALK__HELP + ".list"
    O19_WALK_INFO = O19_WALK__HELP + ".info"
    # O19_WALK_SIM = O19_WALK__HELP + ".sim" # TODO implement me
    O19_WALK_SET = O19_WALK__HELP + ".set"
    O19_WALK_RESET = O19_WALK__HELP + ".reset"
    O19_WALK_STOP = O19_WALK__HELP + ".stop"
    O19_WALK_EXIT = O19_WALK__HELP + ".exit"

    O19_WALK_INIT = O19_WALK__HELP + ".init"

    O19_HH_WALK_HELP = {
        O19_WALK__HELP: ': Show this help message',
        # O19_WALK_SIM: ' [sim]: Clear ot set a sim for all further commands. If set it will be used instead of the current sim.',
        O19_WALK_LIST: ' [filter]: List all or only walk styles matching "filter" (case insensitive)',
        O19_WALK_INFO: ' [sim]: Show the default (and current if available) walk styles.',
        O19_WALK_SET: ' [style] [sim]: Change the walk style to style_id (as seen in ' + O19_WALK_LIST + '. Usually the first 2-3 digits are sufficient.',
        O19_WALK_STOP: ' [sim]: Remove the previously applied walk style for this sim.',
        O19_WALK_EXIT: ' : Remove all previously applied walk styles.',
        O19_WALK_RESET: ' [sim]: Clear all WalkstyleRequests for a sim. If the PIE menu shows only "WW" and no option to "Go Here" this should fix it.',
        O19_WALK_INIT: ' : Write a log file with all walk style IDs and names and one with all priorities.',
        '[filter]': ': Optional parameter to filter walk styles.',
        '[style]': ': Required parameter.',
        '[sim]': ': Optional parameter. If it is missing the current sim will be processed. Otherwise the sim_id or the name in the format "Mary Kate#Smith" (for "Mary Kate" (first names) "Smith" (last name)) can be specified.' + \
                 '"M#S" or "Mary#S" for a random match are also supported.',
    }


@sims4.commands.Command(Res.O19_WALK__HELP, command_type=sims4.commands.CommandType.Live)
def o19_hh_dump_help(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        for key, value in Res.O19_HH_WALK_HELP.items():
            output(key + value)
    except Exception as ex:
        output("Error" + str(ex))



@sims4.commands.Command(Res.O19_WALK_LIST, command_type=sims4.commands.CommandType.Live)
def debug_o19_walk_list(walkstyle_filter=None, _connection=None):
    global styles
    output = sims4.commands.CheatOutput(_connection)
    try:
        output(Res.O19_WALK_LIST + "(filter=" + str(walkstyle_filter) + ")")
        time.sleep(0.8)  # Show the message and refresh the UI

        if not styles:
            O19WalkStyle()

        if walkstyle_filter:
            l_walkstyle_filter = walkstyle_filter.lower()

        console_styles = {}
        for hash32, walkstyle in styles.items():
            if not walkstyle_filter or l_walkstyle_filter in walkstyle.lower():
                console_styles.update({walkstyle: hash32})
                # Write 30 elements (~7 lines) to avoid lags (max-out: 8.5 lines)
                if len(console_styles) > 30:
                    output(str(console_styles))
                    console_styles = {}
        output(str(console_styles))

    except Exception as ex:
        output("Error: " + str(ex))


@sims4.commands.Command(Res.O19_WALK_INFO, command_type=sims4.commands.CommandType.Live)
def debug_o19_walk_info(p_sim=None, _connection=None):
    global oh
    output = sims4.commands.CheatOutput(_connection)
    try:
        if not oh:
            oh = O19Helper()

        o19sim: O19Sim = oh.get_sim_all(p_sim)
        output(f"Sim: {o19sim.sim_name}")
        if not o19sim.sim:
            output("Could not get sim object properly.")
            return

        try:
            walkstyle = o19sim.sim.get_default_walkstyle()
            output("Default walkstyle: " + str(walkstyle))
        except Exception as e:
            output("Default walkstyle: n/a")

        try:
            path = o19sim.sim.routing_component.current_path
            walkstyle = o19sim.sim.routing_component.get_walkstyle_for_path(path)
            output("Current walkstyle: " + str(walkstyle))
        except Exception as e:
            output("Current walkstyle: n/a")

        try:
            walkstyle_requests = o19sim.sim.routing_component.get_walkstyle_requests()
            output("Walkstyle requests: " + str(walkstyle_requests))
        except Exception as e:
            output("Current walkstyle: n/a")

    except Exception as ex:
        output("Error: " + str(ex))


@sims4.commands.Command(Res.O19_WALK_SET, command_type=sims4.commands.CommandType.Live)
def debug_o19_walk_set(p_style_id, p_sim_id=None, _connection=None):
    global oh, styles
    output = sims4.commands.CheatOutput(_connection)
    try:
        output(Res.O19_WALK_SET + "(style=" + str(p_style_id) + ", sim=" + str(p_sim_id) + ")")
        if not oh:
            oh = O19Helper()
        o19sim: O19Sim = oh.get_sim_all(p_sim_id)
        if o19sim.sim is None or o19sim.sim_id is None:
            output("Error: sim/sim_id is None!")
            return False
        if not styles:
            O19WalkStyle()

        if p_style_id.isdigit():
            style_id = int(p_style_id)
            if style_id not in styles:
                for hash32, walkstyle in styles.items():
                    if str(hash32).startswith(p_style_id):
                        # multiple IDs may match, use the 1st one
                        style_id = hash32
                        output("Walkstyle: " + str(walkstyle) + " (" + str(hash32) + ")")
                        break
            if style_id not in styles:
                output("Error: Unknown walkstyle!")
                return
        else:
            style_id = None
            for hash32, walkstyle in styles.items():
                if p_style_id.lower() in walkstyle.lower():
                    style_id = hash32
                    output("Walkstyle: " + str(walkstyle) + " (" + str(hash32) + ")")
                    break
            if style_id is None:
                output("Error: Unknown walkstyle!")
                return


        try:
            walkstyle_request = _walk_style_requests.get(o19sim.sim)
            if walkstyle_request is not None:
                walkstyle_request.stop()
        except Exception as e:
            pass

        walkstyle_name = styles.get(style_id)
        walkstyle = Walkstyle(walkstyle_name, style_id)

        walkstyle_request = WalkStyleRequest(o19sim.sim, walkstyle=walkstyle, priority=MAX_INT32)
        walkstyle_request.start()
        _walk_style_requests[o19sim.sim] = walkstyle_request
    except Exception as ex:
        output("Error: " + str(ex))


@sims4.commands.Command(Res.O19_WALK_STOP, command_type=sims4.commands.CommandType.Live)
def debug_o19_walk_stop(p_sim_id=None, _connection=None):
    global oh
    output = sims4.commands.CheatOutput(_connection)
    try:
        output(f"{Res.O19_WALK_STOP}(sim={p_sim_id})")
        if not oh:
            oh = O19Helper()
        o19sim: O19Sim = oh.get_sim_all(p_sim_id)
        walkstyle_request = _walk_style_requests.get(o19sim.sim)
        if walkstyle_request is not None:
            walkstyle_request.stop()
            del _walk_style_requests[o19sim.sim]
    except Exception as ex:
        output("Error: " + str(ex))


# Cleanup all walkstyle requests for a sim
@sims4.commands.Command(Res.O19_WALK_RESET, command_type=sims4.commands.CommandType.Live)
def debug_o19_walk_fix(p_sim_id=None, _connection=None):
    global oh
    output = sims4.commands.CheatOutput(_connection)
    try:
        output(f"{Res.O19_WALK_RESET}(sim={p_sim_id})")
        if not oh:
            oh = O19Helper()
        o19sim: O19Sim = oh.get_sim_all(p_sim_id)
        sim = o19sim.sim
        routing_component = o19sim.sim.routing_component
        _walk_style_requests = routing_component.get_walkstyle_requests()
        for walkstyle_request in _walk_style_requests:
            walkstyle_request.stop()
            del _walk_style_requests[sim]

    except Exception as ex:
        output("Error: " + str(ex))
        _walk_style_requests.clear()


# Cleanup all stored walkstyle requests by this class
@sims4.commands.Command(Res.O19_WALK_EXIT, command_type=sims4.commands.CommandType.Live)
def debug_o19_walk_exit(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        for sim, walkstyle_request in _walk_style_requests:
            if walkstyle_request is not None:
                walkstyle_request.stop()
                del _walk_style_requests[sim]
    except Exception as ex:
        output("Error: " + str(ex))


@sims4.commands.Command(Res.O19_WALK_INIT, command_type=sims4.commands.CommandType.Live)
def debug_o19_walk_init(_connection=None):
    global oh
    output = sims4.commands.CheatOutput(_connection)
    try:
        output(Res.O19_WALK_INIT + "() - writing 'WalkStyle.txt' and 'WalkStylePriority.txt'.")

        if not oh:
            oh = O19Helper(output)
        O19WalkStyle()
        O19WalkStylePriority()
    except Exception as ex:
        output("Error: " + str(ex))


class O19WalkStyle:
    def __init__(self):
        global oh, styles
        if not oh:
            oh = O19Helper()
        try:
            for walkstyle in sims4.resources.list(type=sims4.resources.Types.WALKSTYLE):
                walkstyle = routing.get_walkstyle_name_from_resource(walkstyle)
                styles.update({int(sims4.hash_util.hash32(walkstyle)): walkstyle})
            # Dump everything to a text file
            current_directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            dump_directory = os.path.join(current_directory, Oops19Constants.DIRECTORY_DUMP)
            file_name = os.path.join(dump_directory, 'WalkStyle.txt')
            with open(file_name, 'wt') as fp:
                oh.print_pretty(fp, str(styles))
                fp.close()
        except Exception as ex:
            oh.log("Error: " + str(ex))


class O19WalkStylePriority:
    def __init__(self):
        global oh
        if not oh:
            oh = O19Helper()
        try:
            priorities = {}
            for wsp in WalkStylePriority:
                priorities.update({int(wsp.value): wsp.name})
            # Dump everything to a text file
            current_directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            dump_directory = os.path.join(current_directory, Oops19Constants.DIRECTORY_DUMP)
            file_name = os.path.join(current_directory, 'WalkStylePriority.txt')
            with open(file_name, 'wt') as fp:
                oh.print_pretty(fp, str(priorities))
                fp.close()
        except Exception as ex:
            oh.log("Error: " + str(ex))

