"""
german_luftwaffe_fallschirmjager_mg42 object definition

repo : https://github.com/openmarmot/twe

notes :
Standard Fallschirmjäger squad gun once units were re-equipped.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_mg42")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mg42")
    return z
