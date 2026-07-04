"""
steel_case object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random
import copy

# import custom packages
from engine.world_object import WorldObject
from ai.ai_animated_sprite import AIAnimatedSprite
from engine.object_registry import register_object


@register_object("steel_case")
def create(world, world_coords):
    z = WorldObject(world, ["steel_case"], AIAnimatedSprite)
    w = [
        world_coords[0] + float(random.randint(-7, 7)),
        world_coords[1] + float(random.randint(-7, 7)),
    ]
    z.world_coords = copy.copy(w)
    z.name = "steel_case"
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.speed = 150
    z.ai.rotation_speed = 800
    z.ai.rotate_time_max = 0.8
    z.ai.move_time_max = 0.3
    z.ai.alive_time_max = 300
    z.ai.self_remove = True
    z.ai.only_remove_when_not_visible = True
    z.no_save = True
    return z
