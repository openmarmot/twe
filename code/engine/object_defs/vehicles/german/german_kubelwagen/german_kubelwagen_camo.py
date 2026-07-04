"""
german_kubelwagen_camo object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_kubelwagen_camo")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_kubelwagen", False)
    z.name = "Kubelwagen (camo)"
    z.image_list = ["kubelwagen_camo"]
    return z
