"""
soviet_is_2 object definition

repo : https://github.com/openmarmot/twe

IS-2 model 1944. The straight 120 mm glacis, not the stepped 1943 nose.
Sprite export names: is_2_chassis.png and is_2_turret.png.
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_is_2")
def create(world, world_coords):
    # ref : https://en.wikipedia.org/wiki/IS-2
    z = WorldObject(world, ["is_2_chassis"], AIVehicle)
    z.name = "IS-2"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.requires_afv_training = True
    z.ai.passenger_compartment_ammo_racks = True
    # lower hull. angles are degrees from vertical.
    # lower glacis 100 mm at 30 is about 115 mm line of sight.
    z.ai.vehicle_armor["top"] = [30, 0, 0]
    z.ai.vehicle_armor["bottom"] = [20, 0, 0]
    z.ai.vehicle_armor["left"] = [90, 0, 0]
    z.ai.vehicle_armor["right"] = [90, 0, 0]
    z.ai.vehicle_armor["front"] = [100, 30, 0]
    z.ai.vehicle_armor["rear"] = [60, 41, 0]
    # upper hull. the 1944 glacis is one 120 mm casting at 60 degrees,
    # about 240 mm line of sight.
    z.ai.passenger_compartment_armor["top"] = [30, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [20, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [90, 0, 0]
    z.ai.passenger_compartment_armor["right"] = [90, 0, 0]
    z.ai.passenger_compartment_armor["front"] = [120, 60, 0]
    z.ai.passenger_compartment_armor["rear"] = [60, 49, 0]
    main_turret = engine.world_builder.spawn_object(world, world_coords, "is_2_turret", True)
    z.ai.turrets.append(main_turret)
    main_turret.ai.vehicle = z

    # crew of four. the hull DT sat in a ball on the right of the glacis and
    # was fired by the driver, so it is not a second turret.
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

    # 37 km/h on the road, 19 km/h cross-country. 1 mph = 11.84 game units/s.
    z.ai.max_speed = 272.32
    z.ai.max_offroad_speed = 139.8
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 110
    # hull about 6.8 m. radius 41 is the 3.09 m width.
    z.bounding_circles.append([[-48.0, 0.0], 41])
    z.bounding_circles.append([[-16.0, 0.0], 41])
    z.bounding_circles.append([[16.0, 0.0], 41])
    z.bounding_circles.append([[48.0, 0.0], 41])
    z.weight = 46000
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    # about 820 L with the external drums. game volume is not liters.
    z.ai.fuel_tanks[0].volume = 130
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "diesel")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "kharkiv_v2-is_engine", False)
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
    for b in range(16):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "dtm_magazine", False))
    # 28 rounds. The usual load was 20 OF-471 and 8 BR-471.
    # BR-471B is in the magazine but was not issued in quantity during the war.
    z.ai.ammo_rack_capacity = 28
    for b in range(8):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "122mm_d_25t_magazine", False)
        )
    for b in range(20):
        temp = engine.world_builder.spawn_object(world, world_coords, "122mm_d_25t_magazine", False)
        engine.world_builder.load_magazine(world, temp, "OF-471")
        z.ai.ammo_rack.append(temp)
    # six road wheels a side, split front and rear for the damage check
    z.ai.min_wheels_per_side_front = 2
    z.ai.min_wheels_per_side_rear = 2
    z.ai.max_wheels = 12
    z.ai.max_spare_wheels = 0
    for b in range(3):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "is_2_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "is_2_wheel", False)
        )
        z.ai.rear_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "is_2_wheel", False)
        )
        z.ai.rear_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "is_2_wheel", False)
        )
    return z
