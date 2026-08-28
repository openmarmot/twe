"""
soviet_svt40_sniper object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_svt40_sniper")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "soviet_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_soviet_gear")
    z.ai.is_expert_marksman = True
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "svt40-sniper", False))
    for _ in range(6):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "svt40_magazine", False))
    return z
