"""
45mm_19k object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("45mm_19k")
def create(world, world_coords):
    # ref https://en.wikipedia.org/wiki/45_mm_anti-tank_gun_M1932_(19-K)#Tank_gun_20-K
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "45mm 19k"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 2
    z.ai.mechanical_accuracy_deg = 0.30
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "45mm_19k_magazine", False)
    z.ai.rate_of_fire = 1
    z.ai.reload_speed = 26
    z.ai.range = 4000
    z.ai.type = "cannon"
    z.ai.use_antitank = True
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
