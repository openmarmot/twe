"""
coffee_tin object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
import engine.world_builder
from engine.object_registry import register_object


@register_object("coffee_tin")
def create(world, world_coords):
    z = WorldObject(world, ["coffee_tin"], AIContainer)
    z.is_container = True
    z.volume = 1
    z.name = "coffee_tin"
    z.description = "A tin of coffee"
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    contents = "coffee_beans"
    if random.randint(0, 1) == 1:
        contents = "ground_coffee"
    engine.world_builder.fill_container(world, z, contents)
    return z
