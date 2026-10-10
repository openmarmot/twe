"""
german_afv_crew_mp40 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_afv_crew_mp40")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    z.image_list = [
        "german_afv_crew",
        "german_afv_crew_prone",
        "german_afv_crew_dead",
    ]
    z.ai.is_afv_trained = True
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "bandage", False))
    engine.world_builder.add_standard_loadout(z, world, "mp40")
    return z
