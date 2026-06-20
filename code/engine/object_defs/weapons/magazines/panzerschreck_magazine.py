"""
panzerschreck_magazine object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("panzerschreck_magazine")
def create(world, world_coords):
    z = WorldObject(world, ["panzerfaust_warhead"], AIMagazine)
    z.name = "panzerschreck magazine"
    z.description = "Rocket magazine for Panzerschreck"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["panzerschreck"]
    z.ai.compatible_projectiles = ["panzerschreck"]
    z.ai.capacity = 1
    z.ai.removable = True
    z.ai.disintegrating = True
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z)
    return z
