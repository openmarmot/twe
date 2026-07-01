"""
t34_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("t34_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "T34 Wheel"
    z.ai.compatible_vehicles = ["soviet_t34_85", "soviet_t34_76_model_1943", "german_t34_747r", "german_t34_747r_camo"]
    z.ai.armor = [10, 0, 0]
    return z
