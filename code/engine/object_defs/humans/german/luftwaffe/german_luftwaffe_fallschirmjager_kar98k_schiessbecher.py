"""
german_luftwaffe_fallschirmjager_kar98k_schiessbecher object definition

repo : https://github.com/openmarmot/twe

notes :
Rifle-grenade Kar98k. Fallschirmjäger kept the Schiessbecher in the gruppe.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_kar98k_schiessbecher")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "kar98k_schiessbecher")
    return z
