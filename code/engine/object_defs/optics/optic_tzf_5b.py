"""
optic_tzf_5b object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_optic import AIOptic
from engine.object_registry import register_object


@register_object("optic_tzf_5b")
def create(world, world_coords):
    z = WorldObject(world, ["cucumber"], AIOptic)
    z.name = "TZF 5b Optic"
    z.ai.magnification = 2.5
    z.ai.field_of_view = 25
    z.ai.optical_quality = 1.5
    z.ai.close_range_penalty = 0
    return z
