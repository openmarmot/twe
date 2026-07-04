"""
warehouse object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_building import AIBuilding
from engine.object_registry import register_object


@register_object("warehouse")
def create(world, world_coords):
    z = WorldObject(world, ["warehouse-outside", "warehouse-inside"], AIBuilding)
    z.name = "warehouse"
    z.description = "A large industrial warehouse"
    z.collision_radius = 200
    z.weight = 10000
    z.is_building = True
    z.bounding_circles.append([[-83.0, -269.0], 100])
    z.bounding_circles.append([[104.0, -269.0], 100])
    z.bounding_circles.append([[-83.84615384615384, 286.9230769230769], 100])
    z.bounding_circles.append([[-75.38461538461539, 96.92307692307692], 100])
    z.bounding_circles.append([[-83.84615384615384, -90.76923076923076], 100])
    z.bounding_circles.append([[108.46153846153845, -150.0], 100])
    z.bounding_circles.append([[-70.76923076923077, 2.3076923076923075], 100])
    z.bounding_circles.append([[-80.0, 178.46153846153845], 100])
    z.bounding_circles.append([[-163.07692307692307, -342.3076923076923], 25])
    z.bounding_circles.append([[7.692307692307692, -348.46153846153845], 25])
    z.bounding_circles.append([[174.6153846153846, -350.7692307692308], 25])
    z.bounding_circles.append([[174.6153846153846, -83.07692307692308], 25])
    z.bounding_circles.append([[24.615384615384613, -88.46153846153845], 25])
    z.bounding_circles.append([[-163.07692307692307, -174.6153846153846], 25])
    z.bounding_circles.append([[-18.46153846153846, 357.6923076923077], 25])
    z.bounding_circles.append([[-152.3076923076923, 358.46153846153845], 25])
    return z
