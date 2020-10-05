#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#

from high_heels.utilities.helper_standalone import O19Sim, O19Helper
from high_heels.utilities.manage_sim_object import ManageSimObject
from sims.sim import Sim
import sims4.commands
import sims4.math
import sims4

# Download ATS4_advent2017_21.zip from https://sims4.aroundthesims3.com/objects/special_06.shtml
# To get it working set the walkstyle to "Drone_Fast" and the sim should be moved up a little bit with a slider.
# TS4 uses random walkstyles for short and long distances. Unless this can be fixed use an average distance when travelling with the board.

# 0xFD83DAE3ADD95C5F - Instance IDs for board colors 1 .. 4 - here the 1st is used
# 0xFD83DAE3ADD95C60
# 0xFD83DAE3ADD95C61
# 0xFD83DAE3ADD95C62


@sims4.commands.Command('o19.board.del', command_type=sims4.commands.CommandType.Live)
def o19_board_del(p_sim=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        oh = O19Helper(output=output)
        o19sim: O19Sim = oh.get_sim_all(p_sim)
        output(f"{o19sim.sim_name}")
        sim: Sim = o19sim.sim

        mo = ManageSimObject()
        mo.add(sim=sim)

        output(f"ok")
    except Exception as ex:
        output(f"o19_board_del() - Error: {ex}")


@sims4.commands.Command('o19.board.add', command_type=sims4.commands.CommandType.Live)
def o19_board_add(p_sim=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        oh = O19Helper(output=output)
        o19sim: O19Sim = oh.get_sim_all(p_sim)
        output(f"{o19sim.sim_name}")
        sim: Sim = o19sim.sim

        position = sims4.math.Vector3(0, -0.12, 0)  # Standing behind sim: (-move_to_right) .. move_to_left | (-move_down) .. move_up | (-move_behind) .. move_in_front (only for b__ROOT__)
        orientation = sims4.math.Quaternion(0, 0, 0, 1)
        transformation = sims4.math.Transform(position, orientation)

        mso = ManageSimObject()
        mso.add(sim=sim, obj_definition_id=0xFD83DAE3ADD95C5F, bone_name='b__ROOT__', scale=1.0, transformation=transformation)

        output(f"ok")
    except Exception as ex:
        output(f"o19_board_add() - Error: {ex}")


@sims4.commands.Command('o19.board.any', command_type=sims4.commands.CommandType.Live)
def o19_board_any(obj_definition_id: str, bone_name: str = None, scale: str = None, px=None, py=None, pz=None, qx=None, qy=None, qz=None, qw=None, p_sim=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output(f"Usage: o19.board.any [obj-id] [bone-name] [scale] [px py pz] [qw qx qy qz] [sim]")
    output(f"    obj-id: required;  bone-name(b__ROOT__): optional;  scale(1.0): optional")
    output(f"    px py pz(0/0/0): optional;  qx qy qz qw(0/0/0/1): optional;  sim: optional")
    try:
        oh = O19Helper(output=output)
        o19sim: O19Sim = oh.get_sim_all(p_sim)
        output(f"{o19sim.sim_name}")
        sim: Sim = o19sim.sim

        if not qw:
            orientation = sims4.math.Quaternion(0.0, 0.0, 0.0, 1.0)
        else:
            orientation = sims4.math.Quaternion(float(qx), float(qy), float(qz), float(qw))

        if not pz:
            position = sims4.math.Vector3(0.0, 0.0, 0.0)
        else:
            position = sims4.math.Vector3(float(px), float(py), float(pz))
        transformation = sims4.math.Transform(position, orientation)

        if not scale:
            scale = 1
        else:
            scale = float(1.0)

        if not bone_name:
            bone_name = 'b__ROOT__'

        mso = ManageSimObject()
        mso.add(sim=sim, obj_definition_id=int(obj_definition_id), bone_name=bone_name, scale=scale, transformation=transformation)

        output(f"ok")
    except Exception as ex:
        output(f"o19_board_any() - Error: {ex}")
