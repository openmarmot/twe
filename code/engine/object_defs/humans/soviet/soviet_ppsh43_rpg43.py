"""
soviet_ppsh43_rpg43 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_ppsh43_rpg43")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "soviet_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_soviet_gear")
    engine.world_builder.add_standard_loadout(z, world, "ppsh43")
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "rpg43", False))
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "rpg43", False))
    return z
