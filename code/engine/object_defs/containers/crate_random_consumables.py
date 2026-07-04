"""
crate_random_consumables object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("crate_random_consumables")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "crate", False)
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, random.choice(engine.world_builder.list_consumables), False)
    )
    return z
