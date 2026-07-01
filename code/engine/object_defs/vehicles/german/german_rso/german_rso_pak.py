"""
german_rso_pak object definition

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


@register_object("german_rso_pak")
def create(world, world_coords):
    # ref : https://en.wikipedia.org/wiki/Raupenschlepper_Ost
    # ref : https://truck-encyclopedia.com/ww2/us/dodge-WC-62-63-6x6.php
    z = WorldObject(world, ["rso_pak", "rso_destroyed"], AIVehicle)
    z.name = "Raupenschlepper Ost PAK"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.vehicle_armor["top"] = [5, 0, 0]
    z.ai.vehicle_armor["bottom"] = [5, 0, 0]
    z.ai.vehicle_armor["left"] = [5, 0, 0]
    z.ai.vehicle_armor["right"] = [5, 0, 0]
    z.ai.vehicle_armor["front"] = [5.20, 20, 0]
    z.ai.vehicle_armor["rear"] = [5, 0, 0]
    turret = engine.world_builder.spawn_object(world, world_coords, "251_pak40_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z
    turret.ai.position_offset = [11, 0]
    turret.ai.rotation_range = [-360, 360]
    turret.ai.primary_turret = True

    role = VehicleRole("driver", z)
    role.is_driver = True
    role.seat_visible = True
    role.seat_offset = [-39, -13]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_rotates_with_turret = True
    role.seat_offset = [16.0, -15.0]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    role.seat_visible = True
    role.turret = turret
    role.seat_rotates_with_turret = True
    role.seat_offset = [14.0, 14.0]
    z.ai.vehicle_crew.append(role)

    z.ai.max_speed = 224.96
    z.ai.max_offroad_speed = 177.6
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    z.bounding_circles.append([[-35.0, 0.0], 25])
    z.bounding_circles.append([[-10.0, 0.0], 25])
    z.bounding_circles.append([[18.0, 0.0], 25])
    z.bounding_circles.append([[35.0, 0.0], 25])
    z.weight = 2500
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 114
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "diesel")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "deutz_diesel_65hp_engine", False)
    )
    z.ai.engines[0].ai.exhaust_position_offset = [75, 10]
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_6v", False)
    )
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "german_fuel_can", False))
    z.add_inventory(engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_medical, False))
    z.add_inventory(
        engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_consumables, False)
    )
    z.ai.ammo_rack_capacity = 24
    for b in range(20):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "75mm_pak40_magazine", False)
        )
    for b in range(4):
        temp = engine.world_builder.spawn_object(world, world_coords, "75mm_pak40_magazine", False)
        engine.world_builder.load_magazine(world, temp, "Sprgr_34_75_L48")
        z.ai.ammo_rack.append(temp)
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 8
    z.ai.max_spare_wheels = 0
    for b in range(2):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "rso_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "rso_wheel", False)
        )
        z.ai.rear_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "rso_wheel", False)
        )
        z.ai.rear_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "rso_wheel", False)
        )
    return z
