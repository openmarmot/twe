"""
feldfunk_battery_charger object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_radio import AIRadio
from engine.object_registry import register_object


@register_object("feldfunk_battery_charger")
def create(world, world_coords):
    # ref https://feldfunker-la7sna.com/wehrm_foto.htm
    z = WorldObject(world, ["radio_feldfunk_charger"], AIRadio)
    z.name = "Feldfunk battery charger"
    z.weight = 15
    z.is_large_human_pickup = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
