"""
german_drop_canister object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_container import AIContainer
from engine.object_registry import register_object


@register_object("german_drop_canister")
def create(world, world_coords):
    z = WorldObject(world, ["german_drop_canister"], AIContainer)
    z.is_container = True
    z.is_large_human_pickup = True
    z.name = "german drop canister"
    z.description = "A German airdrop canister"
    z.collision_radius = 20
    z.rotation_angle = float(random.randint(0, 359))
    return z
