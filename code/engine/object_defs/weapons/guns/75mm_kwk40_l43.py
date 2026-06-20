"""
75mm_kwk40_l43 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("75mm_kwk40_l43")
def create(world, world_coords):
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "75mm_kwk40_l43"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.mechanical_accuracy_deg = 0.12
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "75mm_kwk40_l43_magazine", False
    )
    z.ai.rate_of_fire = 1
    z.ai.reload_speed = 20
    z.ai.range = 4000
    z.ai.type = "cannon"
    z.ai.use_antitank = True
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
