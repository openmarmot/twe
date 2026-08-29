"""
stug_iii_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("stug_iii_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "StuG III Wheel"
    z.ai.compatible_vehicles = [
        "german_stug_iii_ausf_g",
        "german_stug_iii_ausf_g_camo1",
    ]
    z.ai.armor = [10, 0, 0]
    return z
