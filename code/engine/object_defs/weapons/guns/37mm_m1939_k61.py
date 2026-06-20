"""
37mm_m1939_k61 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("37mm_m1939_k61")
def create(world, world_coords):
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "37mm_m1939_k61"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 2
    z.ai.mechanical_accuracy_deg = 0.30
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "37mm_m1939_k61_magazine", False
    )
    z.ai.rate_of_fire = 0.9
    z.ai.reload_speed = 15
    z.ai.range = 4000
    z.ai.type = "automatic cannon"
    z.ai.use_antipersonnel = True
    z.ai.use_antitank = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
