"""
is_2_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("is_2_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    # sprite: is_2_turret.png (export of is_2_turret.xcf). position_offset and
    # the muzzle smoke offset need a pass in image_tool.py once that art is in.
    z = WorldObject(world, ["is_2_turret"], AITurret)
    z.name = "IS-2 Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_tsh_17", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 2
    # cast turret. the face and mantlet are round, so no stored slope:
    # a flat 100 mm is the nominal cheek. the mantlet casting runs thicker,
    # about 100-120 mm, and this one front value covers both.
    z.ai.turret_armor["top"] = [30, 0, 0]
    z.ai.turret_armor["bottom"] = [30, 0, 0]
    z.ai.turret_armor["left"] = [90, 20, 0]
    z.ai.turret_armor["right"] = [90, 20, 0]
    z.ai.turret_armor["front"] = [100, 0, 0]
    z.ai.turret_armor["rear"] = [90, 0, 0]
    z.ai.position_offset = [-17.2, 2.0]
    z.image_rotation_offset = [1.6, 53.6]
    z.ai.rotation_range = [-360, 360]
    z.ai.rotation_speed = 14  # electric traverse, full turn about 26 s
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "122mm_d_25t", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-165, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.coaxial_weapon = engine.world_builder.spawn_object(world, world_coords, "dtm", False)
    z.ai.coaxial_weapon.ai.equipper = z
    z.ai.coaxial_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    # separate-loading 25 kg shot plus the charge. about 2 rounds a minute
    # after the drop breech replaced the early screw breech.
    z.ai.primary_weapon_reload_speed = 30
    z.ai.coaxial_weapon_reload_speed = 10
    z.no_save = True
    return z
