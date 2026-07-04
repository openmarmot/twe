"""
optic_sfl_zf_1 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_optic import AIOptic
from engine.object_registry import register_object


@register_object("optic_sfl_zf_1")
def create(world, world_coords):
    z = WorldObject(world, ["cucumber"], AIOptic)
    z.name = "SFL ZF 1 Optic"
    z.ai.magnification = 5
    z.ai.field_of_view = 8
    z.ai.optical_quality = 1.5
    z.ai.close_range_penalty = 0.2
    return z
