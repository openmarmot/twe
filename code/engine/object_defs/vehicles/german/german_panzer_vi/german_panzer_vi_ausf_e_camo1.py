"""
german_panzer_vi_ausf_e_camo1 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_panzer_vi_ausf_e_camo1")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_panzer_vi_ausf_e", False)
    z.image_list = ["panzer_vi_ausf_e_chassis_camo1"]
    z.ai.turrets[0].image_list = ["panzer_vi_ausf_e_turret_camo1"]
    return z
