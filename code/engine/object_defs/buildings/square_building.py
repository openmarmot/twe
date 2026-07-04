"""
square_building object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_building import AIBuilding
from engine.object_registry import register_object


@register_object("square_building")
def create(world, world_coords):
    z = WorldObject(
        world, ["square_building_outside", "square_building_inside"], AIBuilding
    )
    z.name = "square building"
    z.description = "A simple square building"
    z.collision_radius = 60
    z.weight = 10000
    z.is_building = True
    return z
