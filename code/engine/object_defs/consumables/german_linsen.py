"""
german_linsen object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_consumable import AIConsumable
from engine.object_registry import register_object


@register_object("german_linsen")
def create(world, world_coords):
    z = WorldObject(world, ["can"], AIConsumable)
    z.name = "German Linsen"
    z.description = "Canned lentils"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    z.is_consumable = True
    z.ai.health_effect = 9
    z.ai.hunger_effect = -185
    z.ai.thirst_effect = -5
    z.ai.fatigue_effect = -35
    return z
