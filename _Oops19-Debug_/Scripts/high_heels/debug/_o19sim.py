#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

from high_heels.utilities.o19cache import O19Cache

import sims4
import sims4.commands
from high_heels.utilities.o19sim import O19SimV2

o19cache = O19Cache()

class Res:
    CMD_HELP = 'o19.sim'
    CMD_SIM = CMD_HELP + ".sim"

    HELP = {
        CMD_HELP: ': Show this help message',
        CMD_SIM: ' [sim]: Log the selected sim.',
        '[sim]': ': If the parameter is missing the current sim will be processed. Otherwise the sim_id or the name in the format "Mary Kate#Smith" (for "Mary Kate" (first names) "Smith" (last name)) can be specified.' + \
                 '"M#S" or "Mary#S" for a random match are also supported.',
    }


@sims4.commands.Command(Res.CMD_HELP, command_type=sims4.commands.CommandType.Live)
def o19_sim_test(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        for key, value in Res.HELP.items():
            output(f"{key}{value}")
    except Exception as ex:
        output(f"{Res.CMD_HELP}() Error: {ex}")


@sims4.commands.Command(Res.CMD_SIM, command_type=sims4.commands.CommandType.Live)
def o19_sim_test(p_sim=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        output(f"{Res.CMD_SIM}({p_sim})")
        o19sim = O19SimV2(p_sim)

        # TODO Fix the cache
        #if o19cache.get(o19sim.sim):
        #    output("Sim already in cache.")
        #    o19sim = o19cache.get(o19sim.sim)
        #else:
        #    output("Adding sim to cache.")
        #    o19cache.add(o19sim.sim, o19sim)

        output(f"sim_id: {o19sim.sim_id}")
        output(f"sim_name: {o19sim.sim_name}")
        output(f"sim_filename: {o19sim.sim_filename}")
    except Exception as ex:
        output(f"{Res.CMD_SIM}() Error: {ex}")
