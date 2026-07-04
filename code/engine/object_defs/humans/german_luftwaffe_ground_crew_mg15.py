"""
german_luftwaffe_ground_crew_mg15 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_ground_crew_mg15")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    z.ai.morale = 95
    z.image_list = [
        "luftwaffe_ground_crew",
        "luftwaffe_ground_crew_prone",
        "luftwaffe_ground_crew_dead",
    ]
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    engine.world_builder.add_standard_loadout(z, world, "mg15")
    return z
