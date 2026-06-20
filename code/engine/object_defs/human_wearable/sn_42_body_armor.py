"""
sn_42_body_armor object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wearable import AIWearable
from engine.object_registry import register_object


@register_object("sn_42_body_armor")
def create(world, world_coords):
    z = WorldObject(world, ["sn_42_body_armor"], AIWearable)
    z.name = "SN 42 Body Armor"
    z.minimum_visible_scale = 0.4
    z.weight = 0.98
    z.is_wearable = True
    z.ai.wearable_region = "upper_body"
    z.ai.armor["top"] = [0, 0, 0]
    z.ai.armor["bottom"] = [0, 0, 0]
    z.ai.armor["left"] = [0, 0, 0]
    z.ai.armor["right"] = [0, 0, 0]
    z.ai.armor["front"] = [3, 0, 0]
    z.ai.armor["rear"] = [0, 0, 0]
    z.rotation_angle = float(random.randint(0, 359))
    return z
