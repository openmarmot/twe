"""
kar98k-zf41 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("kar98k-zf41")
def create(world, world_coords):
    # squad marksman rifle. 1.5x long-eye-relief ZF41, not a sniper rifle
    z = WorldObject(world, ["kar98k-zf41"], AIGun)
    z.name = "kar98k-zf41"
    z.description = "A Kar98k with a 1.5x ZF41 sharpshooter scope"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.scope = True
    z.ai.scope_magnification = 1.5
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "kar98k_magazine", False)
    z.ai.rate_of_fire = 2.5
    z.ai.reload_speed = 5
    z.ai.range = 2418
    z.ai.type = "rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
