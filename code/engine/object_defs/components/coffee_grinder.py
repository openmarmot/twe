"""
coffee_grinder object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_coffee_grinder import AICoffeeGrinder
from engine.object_registry import register_object


@register_object("coffee_grinder")
def create(world, world_coords):
    z = WorldObject(world, ["coffee_grinder"], AICoffeeGrinder)
    z.name = "coffee_grinder"
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    z.no_update = True
    return z
