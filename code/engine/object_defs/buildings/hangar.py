"""
hangar object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_building import AIBuilding
from engine.object_registry import register_object


@register_object("hangar")
def create(world, world_coords):
    z = WorldObject(world, ["hangar_outside", "hangar_inside"], AIBuilding)
    z.name = "hangar"
    z.description = "A large aircraft hangar"
    z.collision_radius = 600
    z.weight = 10000
    z.is_building = True
    return z
