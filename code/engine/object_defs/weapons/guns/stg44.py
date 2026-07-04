"""
stg44 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("stg44")
def create(world, world_coords):
    z = WorldObject(world, ["stg44"], AIGun)
    z.name = "stg44"
    z.description = "A German StG 44 assault rifle"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "stg44_magazine", False)
    z.ai.rate_of_fire = 0.1
    z.ai.reload_speed = 7
    z.ai.range = 1913
    z.ai.type = "assault rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
