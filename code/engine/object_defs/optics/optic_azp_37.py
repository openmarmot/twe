"""
optic_azp_37 object definition

repo : https://github.com/openmarmot/twe

notes :
AZP-37-1 computing collimator for the 37 mm M1939 (61-K).
One power, used for direct aim. Not a tank telescope.
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_optic import AIOptic
from engine.object_registry import register_object


@register_object("optic_azp_37")
def create(world, world_coords):
    z = WorldObject(world, ["cucumber"], AIOptic)
    z.name = "AZP-37-1"
    z.ai.magnification = 1
    z.ai.field_of_view = 40
    z.ai.optical_quality = 1.0
    z.ai.close_range_penalty = 0
    return z
