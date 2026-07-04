"""
german_field_shovel object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_throwable import AIThrowable
from engine.object_registry import register_object


@register_object("german_field_shovel")
def create(world, world_coords):
    z = WorldObject(world, ["german_field_shovel"], AIThrowable)
    z.name = "german field shovel"
    z.minimum_visible_scale = 0.4
    z.is_throwable = True
    z.ai.speed = 112
    z.ai.max_speed = 112
    z.ai.maxTime = 2
    z.ai.range = 310
    z.rotation_angle = float(random.randint(0, 359))
    return z
