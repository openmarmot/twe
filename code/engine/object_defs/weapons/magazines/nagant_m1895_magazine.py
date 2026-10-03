"""
nagant_m1895_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("nagant_m1895_magazine")
def create(world, world_coords):
    # the cylinder. spare "magazines" are loose-round refills
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "nagant_m1895_magazine"
    z.description = "Seven rounds of 7.62x38mmR for the Nagant revolver"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["nagant_m1895"]
    z.ai.compatible_projectiles = ["7.62x38R"]
    z.ai.capacity = 7
    z.ai.removable = False
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
