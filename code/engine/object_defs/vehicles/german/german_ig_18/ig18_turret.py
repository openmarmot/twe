"""
ig18_turret object definition

repo : https://github.com/openmarmot/twe

notes :
The leIG 18 does not pivot the trail for its traverse. A screw slides
the top carriage along the axle, and the rear of that carriage is
hinged to the box trail, so the barrel yaws. Published traverse is
12 degrees total. The sprite pivot is that hinge.
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("ig18_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["ig18_turret"], AITurret)
    z.name = "leIG 18"
    z.ai.gun_sight = engine.world_builder.spawn_object(
        world, world_coords, "optic_rbl_f16", False
    )
    z.is_turret = True
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 2
    # fixed shield: front plate with a mild rake, and side cheeks
    # that turn back toward the wheels. the upper flap is steeper
    # when it is raised, and it folds, so it is not its own face.
    # thickness is an estimate. rear is open.
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [0, 0, 0]
    z.ai.turret_armor["left"] = [4, 10, 0]
    z.ai.turret_armor["right"] = [4, 10, 0]
    z.ai.turret_armor["front"] = [4, 15, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    # hinge sits on the front of the trail, 10 px forward of the
    # chassis center. barrel art points up. nudge in image_tool.
    z.ai.position_offset = [-19, 0]
    # pivot is the rear of the cradle, 10 px below the turret image center
    z.image_rotation_offset = [0, 10]
    z.ai.rotation_range = [-6, 6]
    z.ai.rotation_speed = 5  # traversing screw
    z.ai.primary_weapon = engine.world_builder.spawn_object(
        world, world_coords, "75mm_leig18", False
    )
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    # muzzle is about 21 px forward of the hinge
    z.ai.primary_weapon.ai.smoke_offset = [-21, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    # about 7.5 rpm. the piece could do 8-12. the Pak 40 waits 20 s.
    z.ai.primary_weapon_reload_speed = 8
    z.no_save = True
    return z
