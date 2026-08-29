"""
soviet_afv_crew_tt33 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_afv_crew_tt33")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "soviet_soldier", False)
    z.ai.is_afv_trained = True
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "bandage", False))
    engine.world_builder.add_standard_loadout(z, world, "tt33")
    return z
