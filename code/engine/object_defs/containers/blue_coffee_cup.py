"""
blue_coffee_cup object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
from engine.object_registry import register_object


@register_object("blue_coffee_cup")
def create(world, world_coords):
    z = WorldObject(world, ["blue_coffee_cup"], AIContainer)
    z.is_container = True
    z.volume = 0.3
    z.name = "blue_coffee_cup"
    z.description = "A blue coffee cup"
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    return z
