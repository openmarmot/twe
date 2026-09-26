"""
vg1_5 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("vg1_5")
def create(world, world_coords):
    # Gustloff Volkssturmgewehr, early 1945. semi-auto only, StG 44 magazine
    z = WorldObject(world, ["vg1_5"], AIGun)
    z.name = "vg1_5"
    z.description = "A Gustloff VG 1-5 Volkssturm rifle"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    z.ai.mechanical_accuracy = 3
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "stg44_magazine", False)
    z.ai.rate_of_fire = 1.1
    z.ai.reload_speed = 8
    z.ai.range = 1813
    z.ai.type = "semi auto rifle"
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
