"""
luger_p08 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("luger_p08")
def create(world, world_coords):
    z = WorldObject(world, ["walther_p38"], AIGun)
    z.name = "Luger P08"
    z.description = "A Luger P08 pistol"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 4
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "luger_p08_magazine", False)
    z.ai.rate_of_fire = 0.7
    z.ai.reload_speed = 5
    z.ai.range = 604
    z.ai.type = "pistol"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
