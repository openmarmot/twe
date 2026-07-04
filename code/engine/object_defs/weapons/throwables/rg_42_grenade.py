"""
rg_42_grenade object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_throwable import AIThrowable
from engine.object_registry import register_object


@register_object("rg_42_grenade")
def create(world, world_coords):
    z = WorldObject(world, ["rg_42_grenade"], AIThrowable)
    z.name = "RG-42 Grenade"
    z.description = "A Soviet RG-42 fragmentation grenade"
    z.minimum_visible_scale = 0.4
    z.is_grenade = True
    z.is_throwable = True
    z.ai.explosive = True
    z.ai.shrapnel_count = 15
    z.ai.explosion_radius = 20
    z.ai.max_speed = 150
    z.ai.max_flight_time = 2.0
    z.ai.range = 310
    z.ai.has_fuse = True
    z.ai.fuse_max_time = 3
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
