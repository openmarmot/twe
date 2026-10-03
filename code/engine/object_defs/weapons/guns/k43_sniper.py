"""
k43-sniper object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("k43-sniper")
def create(world, world_coords):
    # selected K43 with the 4x ZF4. deliberate semi-auto, same magazine as the infantry rifle
    z = WorldObject(world, ["k43-sniper"], AIGun)
    z.name = "k43-sniper"
    z.description = "A K43 sniper rifle with a 4x ZF4 scope"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 1
    z.ai.scope = True
    z.ai.scope_magnification = 4
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "k43_magazine", False)
    z.ai.rate_of_fire = 1.4
    z.ai.reload_speed = 6
    z.ai.range = 2500
    z.ai.type = "semi auto rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
