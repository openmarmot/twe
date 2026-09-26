"""
mosin_nagant-sniper object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("mosin_nagant-sniper")
def create(world, world_coords):
    # selected 91/30 with the 3.5x PU. slower aimed fire than the infantry rifle
    z = WorldObject(world, ["mosin_nagant-sniper"], AIGun)
    z.name = "mosin_nagant-sniper"
    z.description = "A Mosin-Nagant sniper rifle with a 3.5x PU scope"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.scope = True
    z.ai.scope_magnification = 3.5
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "mosin_magazine", False)
    z.ai.rate_of_fire = 3.9
    z.ai.reload_speed = 6
    z.ai.range = 2500
    z.ai.type = "rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
