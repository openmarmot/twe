"""
dirt object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_animated_sprite import AIAnimatedSprite
from engine.object_registry import register_object


@register_object("dirt")
def create(world, world_coords):
    z = WorldObject(world, ["small_dirt"], AIAnimatedSprite)
    z.name = "dirt"
    z.minimum_visible_scale = 0.4
    z.is_particle_effect = True
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.speed = 0
    z.ai.rotation_speed = 0
    z.ai.rotate_time_max = 0
    z.ai.move_time_max = 0
    z.ai.alive_time_max = 75
    z.ai.self_remove = True
    z.ai.only_remove_when_not_visible = True
    z.no_save = True
    return z
