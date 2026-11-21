"""
german_luftwaffe_ground_crew_ppsh41 object definition

repo : https://github.com/openmarmot/twe

notes :
Captured PPSh-41. Common in Eastern Front alarm units that
armed themselves from the battlefield.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_ground_crew_ppsh41")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_ground_crew", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "ppsh41")
    return z
