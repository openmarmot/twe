"""
cupboard object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
import engine.world_builder
from engine.object_registry import register_object


@register_object("cupboard")
def create(world, world_coords):
    z = WorldObject(world, ["cupboard"], AIContainer)
    z.is_container = True
    z.is_large_human_pickup = True
    z.name = "cupboard"
    z.description = "A wooden cupboard"
    z.collision_radius = 20
    z.rotation_angle = float(random.randint(0, 359))
    z.volume = 100
    z.no_update = True

    if random.randint(0, 1) == 1:
        z.ai.inventory.append(
            engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_household_items, False)
        )
        z.ai.inventory.append(
            engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_household_items, False)
        )
    if random.randint(0, 1) == 1:
        z.ai.inventory.append(
            engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_consumables, False)
        )
    return z
