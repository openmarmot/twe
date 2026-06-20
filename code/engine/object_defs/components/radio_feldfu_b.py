"""
radio_feldfu_b object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_radio import AIRadio
import engine.world_builder
from engine.object_registry import register_object


@register_object("radio_feldfu_b")
def create(world, world_coords):
    # ref https://feldfunker-la7sna.com/wehrm_foto.htm
    z = WorldObject(world, ["radio_feldfunk"], AIRadio)
    z.name = "Feldfunk.b"
    z.is_radio = True
    z.weight = 15
    z.is_large_human_pickup = True
    # z.ai.frequency_range=[90.57,109.45]
    z.ai.frequency_range = [0, 10]
    z.ai.battery = engine.world_builder.spawn_object(world, world_coords, "battery_feldfunk_2v", False)
    z.rotation_angle = float(random.randint(0, 359))
    return z
