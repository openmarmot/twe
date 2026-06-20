"""
german_panzerjager_tiger_p_elefant_camo1 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_panzerjager_tiger_p_elefant_camo1")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(
        world, world_coords, "german_panzerjager_tiger_p_elefant", False
    )
    z.image_list = ["elefant_camo_1"]
    return z
