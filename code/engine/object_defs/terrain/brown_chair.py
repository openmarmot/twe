"""
brown_chair object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("brown_chair")
def create(world, world_coords):
    z = WorldObject(world, ["brown_chair"], AINone)
    z.name = "brown_chair"
    z.minimum_visible_scale = 0.4
    z.is_furniture = True
    z.is_large_human_pickup = True
    z.rotation_angle = float(random.randint(0, 359))
    z.no_update = True
    return z
