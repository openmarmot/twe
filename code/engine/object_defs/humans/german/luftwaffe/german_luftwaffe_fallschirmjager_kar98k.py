"""
german_luftwaffe_fallschirmjager_kar98k object definition

repo : https://github.com/openmarmot/twe

notes :
The rifle most Fallschirmjäger actually carried. The FG 42 did not replace it.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_kar98k")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "kar98k")
    return z
