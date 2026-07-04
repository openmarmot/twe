"""
dani object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_dani import AIDani
from engine.object_registry import register_object


@register_object("dani")
def create(world, world_coords):
    # dani cat. wow!
    z = WorldObject(world, ["dani"], AIDani)
    z.name = "Dani"
    z.ai.speed = 40
    z.collision_radius = 15
    z.is_large_human_pickup = True
    z.large_pickup_offset = [-3, 12]
    return z
