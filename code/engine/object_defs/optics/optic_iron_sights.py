"""
optic_iron_sights object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_optic import AIOptic
from engine.object_registry import register_object


@register_object("optic_iron_sights")
def create(world, world_coords):
    z = WorldObject(world, ["cucumber"], AIOptic)
    z.name = "Iron Sights"
    z.ai.magnification = 1
    z.ai.field_of_view = 40
    z.ai.optical_quality = 0.7
    z.ai.close_range_penalty = 0
    return z
