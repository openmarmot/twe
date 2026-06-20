"""
gun_carriage_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("gun_carriage_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "Gun Carriage Wheel"
    z.ai.compatible_vehicles = ["soviet_37mm_m1939_61k_aa_gun_carriage"]
    return z
