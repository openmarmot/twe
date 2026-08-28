"""
german_mechanic object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_mechanic")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_random_pistol_to_inventory(z, world)
    z.ai.is_mechanic = True
    return z
