"""
mg151_15_belt object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_magazine import AIMagazine
import engine.world_builder
from engine.object_registry import register_object


@register_object("mg151_15_belt")
def create(world, world_coords):
    # Disintegrating Gurt 151. 200 rounds is the common motor-cannon belt.
    z = WorldObject(world, ["stg44_magazine"], AIMagazine)
    z.name = "MG 151/15 belt"
    z.description = "A 200-round disintegrating belt for the MG 151/15"
    z.minimum_visible_scale = 0.4
    z.is_gun_magazine = True
    z.ai.compatible_guns = ["mg151_15", "mg151_15_drilling"]
    z.ai.compatible_projectiles = [
        "15x96_Pzgr",
        "15x96_H-Pzgr",
        "15x96_HE",
    ]
    z.ai.capacity = 200
    z.ai.disintegrating = True
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.load_magazine(world, z, "15x96_Pzgr", True)
    return z
