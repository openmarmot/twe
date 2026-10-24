"""
german_waffen_ss_stg44_zf4 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_waffen_ss_stg44_zf4")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_waffen_ss_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    z.ai.is_expert_marksman = True
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "stg44-zf4", False))
    for _ in range(6):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "stg44_magazine", False))
    return z
