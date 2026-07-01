"""
t20_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("t20_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "T20 Wheel"
    z.ai.compatible_vehicles = ["soviet_t20"]
    z.ai.armor = [5, 0, 0]
    return z
