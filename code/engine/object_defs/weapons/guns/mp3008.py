"""
mp3008 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("mp3008")
def create(world, world_coords):
    # stamped Sten copy, spring 1945. about 460 rpm
    z = WorldObject(world, ["mp3008"], AIGun)
    z.name = "mp3008"
    z.description = "A late-war MP 3008 submachine gun"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 4
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "mp3008_magazine", False)
    z.ai.rate_of_fire = 0.13
    z.ai.reload_speed = 8
    z.ai.range = 1209
    z.ai.type = "submachine gun"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
