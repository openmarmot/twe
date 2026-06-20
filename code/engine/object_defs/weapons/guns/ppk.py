"""
ppk object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("ppk")
def create(world, world_coords):
    z = WorldObject(world, ["ppk"], AIGun)
    z.name = "ppk"
    z.description = "A Walther PPK pistol"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 5
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "ppk_magazine", False)
    z.ai.rate_of_fire = 0.7
    z.ai.reload_speed = 5
    z.ai.range = 604
    z.ai.type = "pistol"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
