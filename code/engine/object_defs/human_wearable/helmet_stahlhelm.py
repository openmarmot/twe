"""
helmet_stahlhelm object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wearable import AIWearable
from engine.object_registry import register_object


@register_object("helmet_stahlhelm")
def create(world, world_coords):
    z = WorldObject(world, ["helmet_stahlhelm"], AIWearable)
    z.name = "helmet_stahlhelm"
    z.minimum_visible_scale = 0.4
    z.weight = 0.98
    z.is_wearable = True
    z.ai.wearable_region = "head"
    z.ai.armor["top"] = [3, 0, 0]
    z.ai.armor["bottom"] = [0, 0, 0]
    z.ai.armor["left"] = [3, 0, 0]
    z.ai.armor["right"] = [3, 0, 0]
    z.ai.armor["front"] = [3, 0, 0]
    z.ai.armor["rear"] = [3, 0, 0]
    z.rotation_angle = float(random.randint(0, 359))
    return z
