"""
bandage object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_medical import AIMedical
from engine.object_registry import register_object


@register_object("bandage")
def create(world, world_coords):
    z = WorldObject(world, ["bandage"], AIMedical)
    z.name = "bandage"
    z.description = "A roll of medical bandage"
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    z.is_medical = True
    z.ai.health_effect = 50
    z.ai.hunger_effect = 0
    z.ai.thirst_effect = 0
    z.ai.fatigue_effect = 0
    return z
