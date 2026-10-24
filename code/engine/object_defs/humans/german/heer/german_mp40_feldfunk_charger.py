"""
german_mp40_feldfunk_charger object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_mp40_feldfunk_charger")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mp40")
    charger = engine.world_builder.spawn_object(world, world_coords, "feldfunk_battery_charger", True)
    z.ai.large_pickup = charger
    return z
