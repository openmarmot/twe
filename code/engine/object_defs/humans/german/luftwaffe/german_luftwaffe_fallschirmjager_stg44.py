"""
german_luftwaffe_fallschirmjager_stg44 object definition

repo : https://github.com/openmarmot/twe

notes :
StG 44. Issued to some Fallschirmjäger and Hermann Göring
panzergrenadier units in 1945. The Kar98k stayed the majority rifle.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_stg44")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "stg44")
    return z
