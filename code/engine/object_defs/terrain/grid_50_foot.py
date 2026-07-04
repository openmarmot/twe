"""
grid_50_foot object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("grid_50_foot")
def create(world, world_coords):
    z = WorldObject(world, ["grid_50_foot"], AINone)
    z.name = "grid_50_foot"
    z.weight = 250
    z.rotation_angle = 0
    z.no_update = True
    return z
