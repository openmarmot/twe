"""
small_flash object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random
import copy

# import custom packages
from engine.world_object import WorldObject
from ai.ai_animated_sprite import AIAnimatedSprite
from engine.object_registry import register_object


@register_object("small_flash")
def create(world, world_coords):
    z = WorldObject(world, ["explosion_flash"], AIAnimatedSprite)
    w = [
        world_coords[0] + float(random.randint(-7, 7)),
        world_coords[1] + float(random.randint(-7, 7)),
    ]
    z.world_coords = copy.copy(w)
    z.name = "small_flash"
    z.minimum_visible_scale = 0.2
    z.is_particle_effect = True
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.speed = 15
    z.ai.rotation_speed = random.randint(400, 500)
    z.ai.rotate_time_max = 1.8
    z.ai.move_time_max = 3
    z.ai.alive_time_max = 3
    z.ai.self_remove = True
    z.no_save = True
    return z
