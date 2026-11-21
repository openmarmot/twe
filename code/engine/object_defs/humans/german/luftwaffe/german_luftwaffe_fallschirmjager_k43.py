"""
german_luftwaffe_fallschirmjager_k43 object definition

repo : https://github.com/openmarmot/twe

notes :
Gewehr 43. Small numbers reached Fallschirmjäger marksmen and squad leaders.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_k43")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "k43")
    return z
