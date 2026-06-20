"""
german_jagdpanzer_38t_hetzer object definition

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


@register_object("german_jagdpanzer_38t_hetzer")
def create(world, world_coords):
    z = WorldObject(world, ["hetzer_chassis", "hetzer_chassis_destroyed"], AIVehicle)
    z.name = "Jagdpanzer 38t Hetzer"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.requires_afv_training = True
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.vehicle_armor["top"] = [8, 0, 0]
    z.ai.vehicle_armor["bottom"] = [8, 0, 0]
    z.ai.vehicle_armor["left"] = [20, 40, 0]
    z.ai.vehicle_armor["right"] = [20, 40, 0]
    z.ai.vehicle_armor["front"] = [60, 15, 0]
    z.ai.vehicle_armor["rear"] = [8, 70, 0]
    z.ai.passenger_compartment_armor["top"] = [8, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [8, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [20, 40, 0]
    z.ai.passenger_compartment_armor["right"] = [20, 40, 0]
    z.ai.passenger_compartment_armor["front"] = [60, 15, 0]
    z.ai.passenger_compartment_armor["rear"] = [8, 70, 0]
    main_turret = engine.world_builder.spawn_object(world, world_coords, "jagdpanzer_38t_main_gun", True)
    z.ai.turrets.append(main_turret)
    main_turret.ai.vehicle = z
    mg_turret = engine.world_builder.spawn_object(world, world_coords, "remote_mg34_turret", True)
    mg_turret.ai.position_offset = [-65, 13]
    z.ai.turrets.append(mg_turret)
    mg_turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = main_turret
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    z.ai.vehicle_crew.append(role)

    z.ai.max_speed = 367.04
    z.ai.max_offroad_speed = 177.6
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    z.bounding_circles.append([[-35.0, 0.0], 30])
    z.bounding_circles.append([[-11.0, 0.0], 30])
    z.bounding_circles.append([[13.0, 0.0], 30])
    z.bounding_circles.append([[32.0, 0.0], 30])
    z.weight = 16000
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 114
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "diesel")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "kharkiv_v2-34_engine", False)
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
    z.rotation_angle = float(random.randint(0, 359))
    for b in range(10):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))
    z.ai.ammo_rack_capacity = 45
    for b in range(40):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "7.5cm_pak39_L48_magazine", False)
        )
    for b in range(5):
        temp = engine.world_builder.spawn_object(world, world_coords, "7.5cm_pak39_L48_magazine", False)
        engine.world_builder.load_magazine(world, temp, "Sprgr_34_75_L48")
        z.ai.ammo_rack.append(temp)
    z.ai.min_wheels_per_side_front = 2
    z.ai.min_wheels_per_side_rear = 2
    z.ai.max_wheels = 12
    z.ai.max_spare_wheels = 0
    for b in range(3):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzer38t_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzer38t_wheel", False)
        )
        z.ai.rear_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzer38t_wheel", False)
        )
        z.ai.rear_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzer38t_wheel", False)
        )
    return z
