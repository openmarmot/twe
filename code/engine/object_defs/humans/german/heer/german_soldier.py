"""
german_soldier object definition (base)

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
import engine.world_builder
from engine.world_object import WorldObject
from ai.ai_human import AIHuman
import engine.name_gen
from engine.object_registry import register_object


@register_object("german_soldier")
def create(world, world_coords):
    z = WorldObject(
        world, ["german_soldier", "german_soldier_prone", "german_dead"], AIHuman
    )
    z.name = engine.name_gen.get_name("german")
    z.ai.speed = 30
    z.collision_radius = 15
    z.is_human = True
    z.ai.is_small_arms_trained = True

    # belt of MG ammo. fairly rare, waffen ss get a second chance at this
    if random.randint(0, 8) == 0:
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))

    return z
