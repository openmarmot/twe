"""
german_sd_kfz_10_camo object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_sd_kfz_10_camo")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_sd_kfz_10_base", False)
    z.name = "Sd.Kfz.10"
    z.image_list = ["sd_kfz_10_chassis_camo"]
    return z
