"""
civilian_shovel_man object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("civilian_shovel_man")
def create(world, world_coords):
    # a shovel enthusiast
    z = engine.world_builder.spawn_object(world, world_coords, "civilian_man", False)
    z.name = "Mr. Shovel"
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "coffee_tin", False))
    z.add_inventory(
        engine.world_builder.spawn_object(world, world_coords, "german_folding_shovel", False)
    )
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "german_field_shovel", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "bandage", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "bandage", False))
    z.add_inventory(
        engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_consumables_common, False)
    )
    z.add_inventory(
        engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_consumables_common, False)
    )
    return z
