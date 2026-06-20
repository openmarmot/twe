"""
5cm_kwk39_l60 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("5cm_kwk39_l60")
def create(world, world_coords):
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "5 cm KwK 39 L/60"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "5cm_kwk39_l60_magazine", False
    )
    z.ai.rate_of_fire = 0.5
    z.ai.reload_speed = 5
    z.ai.range = 2418
    z.ai.type = "cannon"
    z.ai.use_antitank = True
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
