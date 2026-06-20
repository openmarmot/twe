"""
german_fuel_can object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_fuel_can")
def create(world, world_coords):
    z = WorldObject(world, ["german_fuel_can"], AIContainer)
    z.is_container = True
    z.is_large_human_pickup = True
    z.volume = 20
    z.name = "german_fuel_can"
    z.description = "A German military fuel canister"
    z.rotation_angle = float(random.randint(0, 359))
    engine.world_builder.fill_container(world, z, "gas_80_octane")
    return z
