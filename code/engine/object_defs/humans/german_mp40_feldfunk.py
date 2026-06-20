"""
german_mp40_feldfunk object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_mp40_feldfunk")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mp40")
    radio = engine.world_builder.spawn_object(world, world_coords, "radio_feldfu_b", True)
    z.ai.large_pickup = radio
    return z
