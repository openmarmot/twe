"""
jagdpanzer_38t_main_gun object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("jagdpanzer_38t_main_gun")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["jagdpanzer_38t_main_gun", "jagdpanzer_38t_main_gun"], AITurret)
    z.name = "Jagdpanzer 38t Main Gun"
    z.is_turret = True
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_sfl_zf_1", False)
    z.ai.vehicle_mount_side = "front"
    z.ai.turret_accuracy = 1
    z.ai.turret_armor["top"] = [70, 60, 0]
    z.ai.turret_armor["bottom"] = [70, 60, 0]
    z.ai.turret_armor["left"] = [70, 60, 0]
    z.ai.turret_armor["right"] = [70, 60, 0]
    z.ai.turret_armor["front"] = [70, 60, 0]
    z.ai.turret_armor["rear"] = [70, 60, 0]
    z.ai.position_offset = [-45, 10]
    z.ai.rotation_range = [-20, 20]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "7.5cm_pak39_L48", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-83, -1]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 20
    z.no_save = True
    return z
