"""
is_2_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("is_2_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "IS-2 Wheel"
    z.ai.compatible_vehicles = ["soviet_is_2"]
    z.ai.armor = [10, 0, 0]
    return z
