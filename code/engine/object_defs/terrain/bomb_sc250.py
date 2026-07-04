"""
bomb_sc250 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("bomb_sc250")
def create(world, world_coords):
    z = WorldObject(world, ["sc250"], AINone)
    z.name = "bomb_sc250"
    z.weight = 250
    z.rotation_angle = float(random.randint(0, 359))
    z.no_update = True
    return z
