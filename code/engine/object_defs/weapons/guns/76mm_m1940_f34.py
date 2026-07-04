"""
76mm_m1940_f34 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("76mm_m1940_f34")
def create(world, world_coords):
    # https://en.wikipedia.org/wiki/76_mm_tank_gun_M1940_F-34
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "76mm_m1940_f34"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 2
    z.ai.mechanical_accuracy_deg = 0.25
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "76mm_m1940_f34_magazine", False
    )
    z.ai.rate_of_fire = 1
    z.ai.reload_speed = 30
    z.ai.range = 4000
    z.ai.type = "cannon"
    z.ai.use_antitank = True
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
