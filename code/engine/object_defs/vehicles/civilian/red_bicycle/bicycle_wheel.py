"""
bicycle_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("bicycle_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "Bicycle Wheel"
    z.ai.compatible_vehicles = ["red_bicycle", "german_military_bicycle"]
    return z
