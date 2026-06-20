"""
kar98k_schiessbecher object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("kar98k_schiessbecher")
def create(world, world_coords):
    # kar98k with a schiessbecher device for rifle grenades
    z = WorldObject(world, ["kar98k"], AIGun)
    z.name = "kar98k"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "kar98k_magazine", False)
    z.ai.rate_of_fire = 1.1
    z.ai.reload_speed = 10
    z.ai.range = 2418
    z.ai.type = "rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
