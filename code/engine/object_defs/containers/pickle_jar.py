"""
pickle_jar object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("pickle_jar")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "jar", False)
    z.name = "pickle jar"
    z.description = "A jar filled with pickles"
    z.minimum_visible_scale = 0.4
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "pickle", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "pickle", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "pickle", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "pickle", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "pickle", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "pickle", False))
    return z
