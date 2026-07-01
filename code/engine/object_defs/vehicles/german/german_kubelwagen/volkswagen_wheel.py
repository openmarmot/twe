"""
volkswagen_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("volkswagen_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "Volkswagen Wheel"
    z.ai.compatible_vehicles = ["german_kubelwagen", "german_kubelwagen_camo"]
    return z
