"""
german_gulaschsuppe object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_consumable import AIConsumable
from engine.object_registry import register_object


@register_object("german_gulaschsuppe")
def create(world, world_coords):
    z = WorldObject(world, ["can"], AIConsumable)
    z.name = "German Gulaschsuppe"
    z.description = "Canned goulash soup"
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    z.is_consumable = True
    z.ai.health_effect = 11
    z.ai.hunger_effect = -215
    z.ai.thirst_effect = -75
    z.ai.fatigue_effect = -40
    return z
