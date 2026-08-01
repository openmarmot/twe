"""
2cm_kwk38_l55 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("2cm_kwk38_l55")
def create(world, world_coords):
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "2 cm KwK 38 L/55"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 10
    z.ai.mechanical_accuracy_deg = 0.20
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "2cm_kwk38_l55_magazine", False
    )
    z.ai.rate_of_fire = 0.13
    z.ai.range = 4000
    z.ai.type = "automatic cannon"
    z.ai.use_antipersonnel = True
    z.ai.use_antitank = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
