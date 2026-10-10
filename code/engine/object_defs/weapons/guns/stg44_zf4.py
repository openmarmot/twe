"""
stg44-zf4 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("stg44-zf4")
def create(world, world_coords):
    # same gun and magazine as the StG 44. The 4x ZF4 tightens aim. Range stays 1913.
    z = WorldObject(world, ["stg44"], AIGun)
    z.name = "stg44-zf4"
    z.description = "A StG 44 with a 4x ZF4 scope"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.scope = True
    z.ai.scope_magnification = 4
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "stg44_magazine", False)
    z.ai.rate_of_fire = 0.1
    z.ai.reload_speed = 7
    z.ai.range = 1913
    z.ai.type = "assault rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
