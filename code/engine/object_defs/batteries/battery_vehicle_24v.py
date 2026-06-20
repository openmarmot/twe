"""
battery_vehicle_24v object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_battery import AIBattery
from engine.object_registry import register_object


@register_object("battery_vehicle_24v")
def create(world, world_coords):
    z = WorldObject(world, ["battery_vehicle_6v"], AIBattery)
    z.name = "battery_vehicle_24v"
    z.weight = 25
    z.rotation_angle = float(random.randint(0, 359))
    return z
