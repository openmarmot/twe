"""
blood_splatter object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_animated_sprite import AIAnimatedSprite
from engine.object_registry import register_object


@register_object("blood_splatter")
def create(world, world_coords):
    z = WorldObject(world, ["blood_splatter"], AIAnimatedSprite)
    z.name = "blood_splatter"
    z.minimum_visible_scale = 0.3
    # not a particle effect so it gets positioned as a
    # default 2, which is under the bodies (containers)
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.speed = 0
    z.ai.rotation_speed = 0
    z.ai.rotate_time_max = 0
    z.ai.move_time_max = 0
    z.ai.alive_time_max = 300
    z.ai.self_remove = True
    z.ai.only_remove_when_not_visible = True
    z.no_save = True
    return z
