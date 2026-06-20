"""
ptrs_41 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("ptrs_41")
def create(world, world_coords):
    z = WorldObject(world, ["ptrs_41"], AIGun)
    z.name = "PTRS 41 Anti-Tank Rifle"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 3
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "ptrs_41_magazine", False)
    z.ai.rate_of_fire = 1.9
    z.ai.reload_speed = 14
    z.ai.range = 2418
    z.ai.type = "rifle"
    # z.ai.use_antipersonnel=True
    z.ai.use_antitank = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
