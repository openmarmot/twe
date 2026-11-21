"""
german_luftwaffe_fallschirmjager_kar98k_panzerfaust_100 object definition

repo : https://github.com/openmarmot/twe

notes :
Panzerfaust 100. The 1945 close-defense issue.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_kar98k_panzerfaust_100")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "kar98k")
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "panzerfaust_100", False))
    return z
