"""
251_wheel object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_wheel import AIWheel
from engine.object_registry import register_object


@register_object("251_wheel")
def create(world, world_coords):
    z = WorldObject(world, ["volkswagen_wheel"], AIWheel)
    z.name = "251 Wheel"
    z.ai.compatible_vehicles = [
        "german_sd_kfz_251",
        "german_sd_kfz_251/1",
        "german_sd_kfz_251/2",
        "german_sd_kfz_251/9",
        "german_sd_kfz_251/9_late",
        "german_sd_kfz_251/22",
        "german_sd_kfz_251/23",
        "german_sd_kfz_222",
        "german_sd_kfz_222_camo",
        "german_sd_kfz_234_base",
        "german_sd_kfz_234/1",
        "german_sd_kfz_234/2",
    ]
    z.ai.armor = [5, 0, 0]
    return z
