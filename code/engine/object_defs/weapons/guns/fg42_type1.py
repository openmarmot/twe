"""
fg42-type1 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("fg42-type1")
def create(world, world_coords):
    z = WorldObject(world, ["fg42-type1"], AIGun)
    z.name = "fg42-type1"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.bipod = True
    z.ai.mechanical_accuracy = 1
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "fg42_type1_magazine", False)
    z.ai.rate_of_fire = 0.06
    z.ai.reload_speed = 7
    z.ai.range = 2418
    z.ai.type = "machine gun"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
