"""
german_luftwaffe_ground_crew_mp40 object definition

repo : https://github.com/openmarmot/twe

notes :
Group leader. Airfield security and flak NCOs were issued the MP 40.
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_ground_crew_mp40")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_ground_crew", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mp40")
    return z
