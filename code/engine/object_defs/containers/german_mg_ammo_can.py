"""
german_mg_ammo_can object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
from engine.object_registry import register_object


@register_object("german_mg_ammo_can")
def create(world, world_coords):
    z = WorldObject(world, ["german_mg_ammo_can"], AIContainer)
    z.is_ammo_container = True
    z.is_large_human_pickup = True
    z.name = "german_mg_ammo_can"
    z.description = "A German machine gun ammo can"
    z.minimum_visible_scale = 0.4
    z.rotation_angle = float(random.randint(0, 359))
    return z
