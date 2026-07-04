"""
g41w_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("g41w_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "g41w_magazine"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["g41w"]
    z.ai.compatible_projectiles = [
        "7.92x57_SSP",
        "7.92x57_SME",
        "7.92x57_SMK",
        "7.92x57_SMKH",
    ]
    z.ai.capacity = 10
    z.ai.removable = True
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
