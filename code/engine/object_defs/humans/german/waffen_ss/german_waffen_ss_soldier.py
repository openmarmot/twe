"""
german_waffen_ss_soldier object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_waffen_ss_soldier")
def create(world, world_coords):
    z = engine.world_builder.spawn_object(world, world_coords, "german_soldier", False)
    z.ai.max_morale = 110
    z.ai.morale = z.ai.max_morale
    z.ai.is_wearing_camo=True
    z.image_list = [
        "ss_soldier",
        "ss_soldier_prone",
        "ss_soldier_dead",
    ]

    # second chance at belt of MG ammo. Also get a chance from base german_soldier
    if random.randint(0, 4) == 0:
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))

    return z
