"""
2cm_kwk38_l55_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("2cm_kwk38_l55_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "2cm KwK 38 L55 Magazine"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["2cm_kwk38_l55"]
    z.ai.compatible_projectiles = ["20x138_API-T", "20x138_HE"]
    z.ai.disintegrating = True
    z.ai.capacity = 10
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
