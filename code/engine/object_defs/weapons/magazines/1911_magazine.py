"""
1911_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("1911_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "1911_magazine"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["1911"]
    z.ai.compatible_projectiles = ["45_ACP"]
    z.ai.capacity = 7
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
