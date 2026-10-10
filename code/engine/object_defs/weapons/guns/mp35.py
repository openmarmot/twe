"""
mp35 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("mp35")
def create(world, world_coords):
    # MP 35/I. Heavier than the MP40, so a touch steadier. Sprite is the MP40.
    z = WorldObject(world, ["mp40"], AIGun)
    z.name = "mp35"
    z.description = "A German MP 35/I submachine gun"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 2
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "mp35_magazine", False)
    # about 540 rpm
    z.ai.rate_of_fire = 0.11
    z.ai.reload_speed = 7
    z.ai.range = 1209
    z.ai.type = "submachine gun"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
