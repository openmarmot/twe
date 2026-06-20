"""
svt40-sniper object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("svt40-sniper")
def create(world, world_coords):
    z = WorldObject(world, ["svt40-sniper"], AIGun)
    z.name = "svt40-sniper"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.scope = True
    z.ai.scope_magnification = 3.5
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "svt40_magazine", False)
    z.ai.mag_capacity = 10
    z.ai.rate_of_fire = 0.8
    z.ai.reload_speed = 10
    z.ai.range = 2500
    z.ai.type = "semi auto rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
