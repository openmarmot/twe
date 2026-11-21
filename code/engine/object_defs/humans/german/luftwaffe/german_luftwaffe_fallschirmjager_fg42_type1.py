"""
german_luftwaffe_fallschirmjager_fg42_type1 object definition

repo : https://github.com/openmarmot/twe

notes :
Early FG 42. Still in veteran Fallschirmjäger hands in 1944.
About 2,000 were made before the type 2.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_fg42_type1")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "fg42-type1")
    return z
