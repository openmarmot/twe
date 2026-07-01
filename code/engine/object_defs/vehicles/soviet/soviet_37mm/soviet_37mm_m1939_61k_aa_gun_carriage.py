"""
soviet_37mm_m1939_61k_aa_gun_carriage object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_37mm_m1939_61k_aa_gun_carriage")
def create(world, world_coords):
    z = WorldObject(world, ["zu_7_carriage", "zu_7_carriage"], AIVehicle)
    z.name = "37mm M1939 61-K AA Gun Carriage"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.is_towed_gun = True
    z.ai.requires_afv_training = True
    z.ai.vehicle_armor["top"] = [0, 0, 0]
    z.ai.vehicle_armor["bottom"] = [0, 0, 0]
    z.ai.vehicle_armor["left"] = [0, 0, 0]
    z.ai.vehicle_armor["right"] = [0, 0, 0]
    z.ai.vehicle_armor["front"] = [0, 0, 0]
    z.ai.vehicle_armor["rear"] = [0, 0, 0]
    turret = engine.world_builder.spawn_object(world, world_coords, "37mm_m1939_61k_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

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

    role = VehicleRole("commander", z)
    role.is_commander = True
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
    z.bounding_circles.append([[0.0, 0.0], 40])
    z.weight = 2100
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.ammo_rack_capacity = 15
    for b in range(10):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "37mm_m1939_k61_magazine", False)
        )
    for b in range(5):
        temp = engine.world_builder.spawn_object(world, world_coords, "37mm_m1939_k61_magazine", False)
        engine.world_builder.load_magazine(world, temp, "37x252_AP-T")
        z.ai.ammo_rack.append(temp)
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 4
    z.ai.max_spare_wheels = 0
    for b in range(2):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "gun_carriage_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "gun_carriage_wheel", False)
        )
    return z
