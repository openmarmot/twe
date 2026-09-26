"""
svt40 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("svt40")
def create(world, world_coords):
    z = WorldObject(world, ["svt40"], AIGun)
    z.name = "svt40"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 2
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "svt40_magazine", False)
    # aimed semi-auto; detachable 10-round magazine
    z.ai.rate_of_fire = 1.0
    z.ai.reload_speed = 5
    z.ai.range = 2418
    z.ai.type = "semi auto rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
