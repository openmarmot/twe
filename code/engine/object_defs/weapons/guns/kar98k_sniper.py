"""
kar98k-sniper object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("kar98k-sniper")
def create(world, world_coords):
    # selected Kar98k with the 4x ZF39. slower aimed fire than the infantry rifle
    z = WorldObject(world, ["kar98k-sniper"], AIGun)
    z.name = "kar98k-sniper"
    z.description = "A Kar98k sniper rifle with a 4x ZF39 scope"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.scope = True
    z.ai.scope_magnification = 4
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "kar98k_magazine", False)
    z.ai.rate_of_fire = 3.5
    z.ai.reload_speed = 5
    z.ai.range = 2500
    z.ai.type = "rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
