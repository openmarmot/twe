"""
cucumber object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_consumable import AIConsumable
from engine.object_registry import register_object


@register_object("cucumber")
def create(world, world_coords):
    z = WorldObject(world, ["cucumber"], AIConsumable)
    z.name = "cucumber"
    z.description = "A green cucumber"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    z.is_consumable = True
    z.ai.health_effect = 5
    z.ai.hunger_effect = -45
    z.ai.thirst_effect = -35
    z.ai.fatigue_effect = -8
    return z
