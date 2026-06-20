"""
7.5cm_pak39_L48_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("7.5cm_pak39_L48_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "7.5 cm Pak 39 L48 Cannon Magazine"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["7.5cm_pak39_L48"]
    z.ai.compatible_projectiles = ["PzGr39_75_L48", "Sprgr_34_75_L48"]
    z.ai.capacity = 1
    z.ai.disintegrating = True
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
