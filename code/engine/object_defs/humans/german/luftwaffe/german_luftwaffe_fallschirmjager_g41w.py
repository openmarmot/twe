"""
german_luftwaffe_fallschirmjager_g41w object definition

repo : https://github.com/openmarmot/twe

notes :
G41(W). A 1943 semi-auto that some Fallschirmjäger still carried in 1944.
The K43 replaced it.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_g41w")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "g41w")
    return z
