"""
panzeriv_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("panzeriv_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "Panzer IV Wheel"
    z.ai.compatible_vehicles = [
        "german_panzer_iv_ausf_g",
        "german_panzer_iv_ausf_h",
        "german_panzer_iv_ausf_j",
    ]
    z.ai.armor = [10, 0, 0]
    return z
