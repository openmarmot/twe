"""
german_luftwaffe_fallschirmjager_mp40 object definition

repo : https://github.com/openmarmot/twe

notes :
Squad leader's weapon in gruppen that did not receive an FG 42.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_mp40")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mp40")
    return z
