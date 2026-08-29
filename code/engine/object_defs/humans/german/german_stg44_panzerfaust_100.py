"""
german_stg44_panzerfaust_100 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_stg44_panzerfaust_100")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "stg44")
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "panzerfaust_100", False))
    return z
