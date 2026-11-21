"""
german_luftwaffe_ground_crew object definition (base)

repo : https://github.com/openmarmot/twe

notes :
Luftwaffe ground troops who were not Fallschirmjäger: airfield
companies, flak gunners fighting as infantry, and 1945 alarm units.
The uniform is the blue-grey Fliegerbluse. Morale is under a Heer
rifleman because these men were not trained as infantry. Weapon
files spawn this body and add the loadout.
"""

# import built in modules
import random

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_ground_crew")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    # airfield and flak troops. rifle drill, not infantry veterans
    z.ai.max_morale = 95
    z.ai.morale = z.ai.max_morale
    z.image_list = [
        "luftwaffe_ground_crew",
        "luftwaffe_ground_crew_prone",
        "luftwaffe_ground_crew_dead",
    ]

    # spare MG 15 saddle drum. ground crews kept aircraft drums on hand.
    # german_soldier can also roll an mg34 belt
    if random.randint(0, 5) == 0:
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg15_drum_magazine", False))

    return z
