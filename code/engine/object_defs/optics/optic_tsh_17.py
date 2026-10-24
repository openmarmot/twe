"""
optic_tsh_17 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_optic import AIOptic
from engine.object_registry import register_object


@register_object("optic_tsh_17")
def create(world, world_coords):
    # D-25T gunner's sight. 4x, 16 degree field, same class as the TSh-16.
    z = WorldObject(world, ["cucumber"], AIOptic)
    z.name = "TSh-17 Optic"
    z.ai.magnification = 4
    z.ai.field_of_view = 16
    z.ai.optical_quality = 0.9
    z.ai.close_range_penalty = 0.2
    return z
