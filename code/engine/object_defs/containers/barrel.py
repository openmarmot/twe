"""
barrel object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
import engine.world_builder
from engine.object_registry import register_object


@register_object("barrel")
def create(world, world_coords):
    z = WorldObject(world, ["barrel"], AIContainer)
    z.is_container = True
    z.volume = 208
    z.name = "barrel"
    z.description = "A wooden barrel"
    z.collision_radius = 15
    z.rotation_angle = float(random.randint(0, 359))
    z.no_update = True
    if random.randint(0, 1) == 1:
        engine.world_builder.fill_container(world, z, "water")
    return z
