#
# License: https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2020 https://github.com/Oops19
#
#


from typing import Union
import objects.system
import sims4.commands
import sims4.math
import sims4.hash_util
import sims4
from sims.sim import Sim
import weakref


class ManageSimObject:
    """
    Simple class to attach an object to a sim and to remove it. Each bone may be equipped with one object.
    Usage:
    mso = ManageSimObject()
    mso.add(sim=sim, obj_definition_id=int(obj_definition_id), bone_name=bone_name, scale=scale, transformation=transformation)
    mso.remove(sim=sim, bone_name=bone_name)

    Return code is 'True' unless an error occurred. The error can be retrieved (and then logged) with:
    exception = mso.e()
    """

    def __init__(self):
        self.exception = None

    def remove(self, sim: Sim, bone_name: str) -> bool:
        try:
            self.exception = None
            self._remove(sim, bone_name)
            return True
        except Exception as e:
            self.exception = e
            return False

    def add(self, sim: Sim, obj_definition_id: Union[int, None] = None, bone_name: Union[str, None] = None, scale: float = 1.0, transformation: Union[sims4.math.Transform, None] = None) -> bool:
        try:
            self.exception = None
            if obj_definition_id is None:
                raise ValueError(f"ManageSimObject.add() obj_definition_id is None")

            obj = objects.system.create_object(obj_definition_id)
            if obj is None:
                raise ValueError(f"ManageSimObject.add() create_object(obj_definition_id) is None")

            if bone_name is None:
                # Use the root bone - likely not useful but a good starting point
                bone_name = 'b__ROOT__'
            bone_hash: int = sims4.hash_util.hash32('b__ROOT__')

            if transformation is None:
                # Create a Null vector - likely not useful but a good starting point
                position = sims4.math.Vector3(0, 0, 0)
                orientation = sims4.math.Quaternion(0, 0, 0, 1)
                transformation = sims4.math.Transform(position, orientation)

            self._remove(sim, bone_name)
            self._add(sim, obj, scale, transformation, bone_hash)
            return True
        except Exception as e:
            self.exception = e
            return False

    def e(self):
        return self.exception

    def _add(self, sim: Sim, obj, scale: float, transformation: sims4.math.Transform, bone_hash: int):
        # TODO rename current_object_set_as_head to current_object_set_as_head_2
        #
        obj.scale = scale
        sim.current_object_set_as_head = weakref.ref(obj)  # setattr(sim, f"object_as_{bone_name}", weakref.ref(obj))
        obj.set_parent(sim, transform=transformation, joint_name_or_hash=bone_hash)

    def _remove(self, sim: Sim, bone_name: str):
        # TODO rename current_object_set_as_head to current_object_set_as_head_2
        # obj = getattr(sim, f"object_as_{bone_name}", None)
        # if obj:
            #obj.destroy(source=sim, cause=f'Destroying existing object set as {bone_name}.')
        if sim.current_object_set_as_head is not None and sim.current_object_set_as_head() is not None:
            sim.current_object_set_as_head().destroy(source=sim, cause=f'Destroying existing object set as Xxx.')
