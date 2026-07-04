"""
molotov_cocktail object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_throwable import AIThrowable
from engine.object_registry import register_object


@register_object("molotov_cocktail")
def create(world, world_coords):
    z = WorldObject(world, ["green_bottle"], AIThrowable)
    z.name = "Molotov Cocktail"
    z.description = "A Molotov cocktail incendiary"
    z.minimum_visible_scale = 0.4
    z.is_grenade = True
    z.is_throwable = True
    z.ai.flammable = True
    z.ai.explode_on_contact = True
    z.ai.flame_amount = 5
    z.ai.max_speed = 150
    z.ai.max_flight_time = 2.0
    z.ai.range = 310
    z.ai.has_fuse = True
    z.ai.fuse_max_time = 4
    z.ai.use_antipersonnel = True
    z.ai.use_antitank = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
