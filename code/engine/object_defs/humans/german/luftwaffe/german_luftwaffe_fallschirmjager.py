"""
german_luftwaffe_fallschirmjager object definition (base)

repo : https://github.com/openmarmot/twe

notes :
Fallschirmjäger. Elite Luftwaffe infantry, morale with the Waffen-SS.
By 1944 most of them fought in the blue-grey Fliegerbluse. The
splinter jump smock is a later skin. The sprite is the ground-crew
uniform until that art exists. Weapon files spawn this body and add
the loadout.
"""

# import built in modules
import random

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_fallschirmjager")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    z.ai.max_morale = 110
    z.ai.morale = z.ai.max_morale
    z.image_list = [
        "luftwaffe_ground_crew",
        "luftwaffe_ground_crew_prone",
        "luftwaffe_ground_crew_dead",
    ]

    # second chance at an MG belt. german_soldier already rolls once.
    # a Fallschirmjäger gruppe carried the gun's ammunition
    if random.randint(0, 4) == 0:
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))

    return z
