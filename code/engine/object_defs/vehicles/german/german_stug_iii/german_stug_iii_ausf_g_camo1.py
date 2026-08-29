"""
german_stug_iii_ausf_g_camo1 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_stug_iii_ausf_g_camo1")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_stug_iii_ausf_g", False)
    z.image_list = ["stug_iii_chassis_camo_1"]
    return z
