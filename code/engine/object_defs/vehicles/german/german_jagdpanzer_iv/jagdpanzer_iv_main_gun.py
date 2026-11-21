"""
jagdpanzer_iv_main_gun object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("jagdpanzer_iv_main_gun")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/jagdpanzer-iv.php
    z = WorldObject(world, ["jagdpanzer_iv_turret", "jagdpanzer_iv_turret"], AITurret)
    z.name = "Jagdpanzer IV Main Gun"
    z.is_turret = True
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_sfl_zf_1a", False)
    z.ai.vehicle_mount_side = "front"
    z.ai.turret_accuracy = 1
    # Saukopfblende: 80 mm cast, face nearly vertical. a stored slope
    # would thicken a center hit. off-square shots already pick up
    # horizontal obliquity. top and bottom are the lid.
    z.ai.turret_armor["top"] = [30, 0, 0]
    z.ai.turret_armor["bottom"] = [30, 0, 0]
    z.ai.turret_armor["left"] = [80, 0, 0]
    z.ai.turret_armor["right"] = [80, 0, 0]
    z.ai.turret_armor["front"] = [80, 0, 0]
    z.ai.turret_armor["rear"] = [80, 0, 0]
    # mantlet center on the glacis, right of the centerline.
    # pivot is the saukopf so the barrel extends forward.
    z.ai.position_offset = [-39.6, 6]
    z.image_rotation_offset = [-0.1, 32.5]
    z.ai.rotation_range = [-10, 10]
    z.ai.rotation_speed = 5  # handwheel
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "7.5cm_pak39_L48", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-71, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 20
    z.no_save = True
    return z
