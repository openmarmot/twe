"""
german_luftwaffe_fallschirmjager_fg42_type2 object definition

repo : https://github.com/openmarmot/twe

notes :
Production FG 42. The Fallschirmjäger selective-fire rifle.
About 5,000 were made. Most squads never received one.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager_fg42_type2")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_fallschirmjager", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "fg42-type2")
    return z
