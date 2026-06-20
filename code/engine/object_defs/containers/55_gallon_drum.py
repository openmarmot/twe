"""
55_gallon_drum object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
import engine.world_builder
from engine.object_registry import register_object


@register_object("55_gallon_drum")
def create(world, world_coords):
    z = WorldObject(world, ["55_gallon_drum"], AIContainer)
    z.is_container = True
    z.volume = 208
    z.name = "55_gallon_drum"
    z.description = "A standard 55 gallon fuel drum"
    z.collision_radius = 15
    z.rotation_angle = float(random.randint(0, 359))
    z.volume = 208.2
    engine.world_builder.fill_container(world, z, "gas_80_octane")
    return z
