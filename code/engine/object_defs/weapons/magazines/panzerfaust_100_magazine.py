"""
panzerfaust_100_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("panzerfaust_100_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["panzerfaust_empty"], AIMagazine)
    z.name = "panzerfaust internal magazine"
    z.description = "Internal magazine for Panzerfaust 100"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["panzerfaust_100"]
    z.ai.compatible_projectiles = ["panzerfaust_100"]
    z.ai.capacity = 1
    z.ai.removable = False
    z.ai.disintegrating = True
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
