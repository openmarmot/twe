"""
75mm_kwk40_l48_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("75mm_kwk40_l48_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "75mm KWK40 L48 Magazine"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["75mm_kwk40_l48"]
    z.ai.compatible_projectiles = ["PzGr39_75_L48", "Sprgr_34_75_L48"]
    z.ai.capacity = 1
    z.ai.disintegrating = True
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
