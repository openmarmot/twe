"""
german_luftwaffe_ground_crew_mg34 object definition

repo : https://github.com/openmarmot/twe

notes :
Flak batteries and Luftwaffe ground units usually had the MG 34
for local defense. The MG 42 went to the field army first.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_ground_crew_mg34")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_ground_crew", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mg34")
    return z
