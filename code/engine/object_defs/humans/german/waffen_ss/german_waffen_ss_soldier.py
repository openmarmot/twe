"""
german_waffen_ss_soldier object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_waffen_ss_soldier")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    z.ai.morale = 110
    z.ai.is_wearing_camo=True
    z.image_list = [
        "ss_soldier",
        "ss_soldier_prone",
        "ss_soldier_dead",
    ]
    return z
