"""
optic_tmfd_7 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_optic import AIOptic
from engine.object_registry import register_object


@register_object("optic_tmfd_7")
def create(world, world_coords):
    z = WorldObject(world, ["cucumber"], AIOptic)
    z.name = "TMFD 7 Optic"
    z.ai.magnification = 2.5
    z.ai.field_of_view = 18
    z.ai.optical_quality = 0.8
    z.ai.close_range_penalty = 0
    return z
