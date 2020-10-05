#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

from high_heels.utilities.helper_standalone import O19Helper
import sims4
import sims4.commands

@sims4.commands.Command('o19.helper.standalone.cache', command_type=sims4.commands.CommandType.Live)
def o19_helper_standalone_cache(sim_name=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        output("o19_helper_standalone_test()")
        oh = O19Helper(output)

        # Refresh the cache every time we use it. Not really needed.
        oh.init_name_cache()
        if sim_name:
            oh.log("Sim " + str(sim_name) + " ==> " + str(oh.get_full_sim_name(sim_name)))
    except Exception as ex:
        output("o19_helper_standalone_test() Error: " + str(ex))

@sims4.commands.Command('o19.helper.standalone.test', command_type=sims4.commands.CommandType.Live)
def o19_helper_standalone_test(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        output("o19_helper_standalone_test()")
        oh_o = O19Helper(output)
        oh_o.log("Hello to console")

        oh_l = O19Helper()
        oh_l.log("Hello to log")
    except Exception as ex:
        output("o19_helper_standalone_test() Error: " + str(ex))
