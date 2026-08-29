"""
soviet_medic object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_medic")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "soviet_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_soviet_gear")
    # sidearm for self-defense; without this medics spawn unarmed and can
    # hit engage-enemy paths with primary_weapon is None
    engine.world_builder.add_standard_loadout(z, world, "tt33")
    z.ai.is_medic = True
    return z
