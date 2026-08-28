"""
civilian_big_cheese object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("civilian_big_cheese")
def create(world, world_coords):
    # big cheese!
    z = engine.world_builder.spawn_object(world, world_coords, "civilian_man", False)
    z.name = "big cheese"
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "adler-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "camembert-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "camembert-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "camembert-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "camembert-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "camembert-cheese", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "bandage", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "bandage", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_drum_magazine", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "panzerfaust_60", False))
    return z
