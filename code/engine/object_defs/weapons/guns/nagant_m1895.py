"""
nagant_m1895 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("nagant_m1895")
def create(world, world_coords):
    # double-action revolver. gate-loaded, so a refill is slower than the TT-33
    z = WorldObject(world, ["nagant_m1895"], AIGun)
    z.name = "nagant_m1895"
    z.description = "A Soviet M1895 Nagant revolver"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 4
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "nagant_m1895_magazine", False)
    z.ai.rate_of_fire = 1.1
    z.ai.reload_speed = 9
    z.ai.range = 604
    z.ai.type = "pistol"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
