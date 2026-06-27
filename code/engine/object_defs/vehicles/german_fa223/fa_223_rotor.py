"""
fa_223_rotor object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_rotor import AIRotor
from engine.object_registry import register_object


@register_object("fa_223_rotor")
def create(world, world_coords):
    z = WorldObject(world, ["fa_223_drache_rotor", "fa_223_drache_rotor"], AIRotor)
    z.name = "FA 223 Drache Rotor"
    z.is_rotor = True
    return z
