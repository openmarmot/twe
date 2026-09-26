"""
soviet_mosin_nagant_sniper object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_mosin_nagant_sniper")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "soviet_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_soviet_gear")
    z.ai.is_expert_marksman = True
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mosin_nagant-sniper", False))
    for _ in range(6):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mosin_magazine", False))
    return z
