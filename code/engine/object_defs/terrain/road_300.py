"""
road_300 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("road_300")
def create(world, world_coords):
    # a road segment
    z = WorldObject(world, ["road_300"], AINone)
    z.name = "road"
    z.weight = 1000
    z.rotation_angle = 0
    z.no_update = True
    return z
