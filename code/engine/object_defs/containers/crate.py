"""
crate object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
import engine.world_builder
from engine.object_registry import register_object


@register_object("crate")
def create(world, world_coords):
    z = WorldObject(world, ["crate"], AIContainer)
    z.is_container = True
    z.is_large_human_pickup = True
    z.name = "crate"
    z.description = "A wooden supply crate"
    z.collision_radius = 20
    z.rotation_angle = float(random.randint(0, 359))
    z.volume = 100
    z.no_update = True
    return z
