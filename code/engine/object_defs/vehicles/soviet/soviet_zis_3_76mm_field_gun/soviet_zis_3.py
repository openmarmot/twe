"""
soviet_zis_3 object definition

repo : https://github.com/openmarmot/twe

notes :
The divisional gun is two spawn identities on the same carriage.
soviet_zis_3_artillery carries 5 BR-350B, 1 solid 76x385_AP, and 24 HE
and starts laid for indirect fire. soviet_zis_3_antitank carries 18 BR-350B,
4 solid 76x385_AP, and 8 HE and starts in direct fire. Both keep indirect
fire available. The T-34-76 still uses 76mm_m1940_f34 and is not part of this split.
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


def _build(world, world_coords, display_name, ap_b_rounds, ap_sp_rounds, he_rounds, indirect_fire_mode):
    """Shared ZiS-3 carriage. BR-350B is the usual AP, 76x385_AP is solid shot, OF-350M is HE."""
    z = WorldObject(world, ["zis_3_carriage"], AIVehicle)
    z.name = display_name
    z.is_vehicle = True
    z.is_towable = True
    z.ai.is_towed_gun = True
    z.ai.requires_afv_training = False
    z.ai.vehicle_armor["top"] = [0, 0, 0]
    z.ai.vehicle_armor["bottom"] = [0, 0, 0]
    z.ai.vehicle_armor["left"] = [6, 22, 0]
    z.ai.vehicle_armor["right"] = [6, 22, 0]
    z.ai.vehicle_armor["front"] = [6, 36, 0]
    z.ai.vehicle_armor["rear"] = [0, 0, 0]
    turret = engine.world_builder.spawn_object(world, world_coords, "soviet_zis_3_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z
    # turret defaults to indirect. antitank guns start ready to shoot what they can see
    turret.ai.primary_weapon.ai.indirect_fire_mode = indirect_fire_mode

    role = VehicleRole("driver", z)
    role.is_driver = True
    role.seat_visible = True
    role.seat_offset = [13, 20]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [7, -9]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    role.seat_visible = True
    role.seat_offset = [13, 15]
    z.ai.vehicle_crew.append(role)

    z.ai.engines.append(engine.world_builder.spawn_object(world, world_coords, "bicycle_pedals", False))
    z.ai.max_speed = 100
    z.ai.max_offroad_speed = 100
    z.ai.open_top = True
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 50
    z.bounding_circles.append([[0.0, 0.0], 25])
    z.weight = 1400
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.ammo_rack_capacity = ap_b_rounds + ap_sp_rounds + he_rounds
    for b in range(ap_b_rounds):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34_magazine", False)
        )
    for b in range(ap_sp_rounds):
        temp = engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34_magazine", False)
        engine.world_builder.load_magazine(world, temp, "76x385_AP")
        z.ai.ammo_rack.append(temp)
    for b in range(he_rounds):
        temp = engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34_magazine", False)
        engine.world_builder.load_magazine(world, temp, "OF-350M")
        z.ai.ammo_rack.append(temp)
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 0
    z.ai.max_wheels = 4
    z.ai.max_spare_wheels = 0
    z.ai.front_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "pak_wheel", False)
    )
    z.ai.front_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "pak_wheel", False)
    )
    return z


@register_object("soviet_zis_3_artillery")
def create_artillery(world, world_coords):
    """Divisional battery load. Mostly OF-350M, starts in indirect fire."""
    return _build(world, world_coords, "ZiS-3 76mm Artillery", 5, 1, 24, True)


@register_object("soviet_zis_3_antitank")
def create_antitank(world, world_coords):
    """Antitank battery load. Mostly BR-350B, starts in direct fire."""
    return _build(world, world_coords, "ZiS-3 76mm Antitank", 18, 4, 8, False)
