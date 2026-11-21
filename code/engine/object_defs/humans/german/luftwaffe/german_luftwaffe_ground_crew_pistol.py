"""
german_luftwaffe_ground_crew_pistol object definition

repo : https://github.com/openmarmot/twe

notes :
Flak gunners and ground staff often had a sidearm and no rifle.
The P38 was the late-war issue pistol. Luftwaffe depots still
held a lot of P08s.
"""

# import built in modules
import random

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_luftwaffe_ground_crew_pistol")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_luftwaffe_ground_crew", False)
    engine.world_builder.add_standard_loadout(z, world, "standard_german_gear")
    # about one in three still drew the older Luger
    if random.randint(0, 2) == 0:
        engine.world_builder.add_standard_loadout(z, world, "luger_p08")
    else:
        engine.world_builder.add_standard_loadout(z, world, "walther_p38")
    return z
