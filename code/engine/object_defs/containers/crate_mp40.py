"""
crate_mp40 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
import engine.world_builder
from engine.object_registry import register_object


@register_object("crate_mp40")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "crate", False)
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mp40_magazine", False))
    return z
