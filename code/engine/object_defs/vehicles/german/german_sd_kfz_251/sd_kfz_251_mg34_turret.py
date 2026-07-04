"""
sd_kfz_251_mg34_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("sd_kfz_251_mg34_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
    z = WorldObject(
        world, ["sd_kfz_251_mg34_turret", "sd_kfz_251_mg34_turret"], AITurret
    )
    z.name = "Sd.Kfz.251 MG34 Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_iron_sights", False)
    z.is_turret = True
    z.ai.small = True
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 10
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [13, 0, 0]
    z.ai.turret_armor["left"] = [6, 22, 0]
    z.ai.turret_armor["right"] = [6, 22, 0]
    z.ai.turret_armor["front"] = [6, 36, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    z.ai.position_offset = [-10, 0]
    z.ai.rotation_range = [-20, 20]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "mg34", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon_reload_speed = 10
    z.ai.primary_turret = True
    z.no_save = True
    return z
