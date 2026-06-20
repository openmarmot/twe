"""
pinus_sylvestris object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_none import AINone
from engine.object_registry import register_object


@register_object("pinus_sylvestris")
def create(world, world_coords):
    # scots pine
    z = WorldObject(world, ["pinus_sylvestris"], AINone)
    z.name = "pinus_sylvestris"
    z.weight = 1000
    z.rotation_angle = float(random.randint(0, 359))
    z.no_update = True
    return z
