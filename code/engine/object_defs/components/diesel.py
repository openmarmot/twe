"""
diesel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("diesel")
def create(world, world_coords):
    z = WorldObject(world, ["small_clear_spill"], AINone)
    z.name = "diesel"
    z.is_liquid = True
    z.is_solid = False
    z.no_update = True
    return z
