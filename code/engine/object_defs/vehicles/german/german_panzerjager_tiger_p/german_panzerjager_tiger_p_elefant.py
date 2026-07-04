"""
german_panzerjager_tiger_p_elefant object definition

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


@register_object("german_panzerjager_tiger_p_elefant")
def create(world, world_coords):
    # a late model Ferdy/Elefant
    # note that 2 of these fought in the battle of berlin !
    z = WorldObject(world, ["elefant"], AIVehicle)
    z.name = "Panzerjager Tiger P Elefant"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.requires_afv_training = True
    z.ai.passenger_compartment_ammo_racks = True
    # [armor in mm, angle in degrees with 0 being vertical, spaced armor in mm]
    # vehicle_armor is the lower half
    # passenger_compartment_armor is the upper half
    z.ai.vehicle_armor["top"] = [30, 0, 0]
    z.ai.vehicle_armor["bottom"] = [20, 0, 0]
    z.ai.vehicle_armor["left"] = [80, 0, 5]
    z.ai.vehicle_armor["right"] = [80, 0, 5]
    z.ai.vehicle_armor["front"] = [
        110,
        45,
        0,
    ]  # 80 on the early models, some sources say the late models were 80+30
    z.ai.vehicle_armor["rear"] = [80, 30, 0]
    z.ai.passenger_compartment_armor["top"] = [30, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [20, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [80, 30, 0]
    z.ai.passenger_compartment_armor["right"] = [80, 30, 0]
    z.ai.passenger_compartment_armor["front"] = [200, 20, 0]
    z.ai.passenger_compartment_armor["rear"] = [80, 30, 0]
    main_turret = engine.world_builder.spawn_object(world, world_coords, "elefant_turret", True)
    z.ai.turrets.append(main_turret)
    main_turret.ai.vehicle = z
    mg_turret = engine.world_builder.spawn_object(world, world_coords, "panzer_vi_ausf_e_hull_mg", True)
    mg_turret.ai.position_offset = [-67.0, 17.0]
    z.ai.turrets.append(mg_turret)
    mg_turret.ai.vehicle = z
    z.ai.radio = engine.world_builder.spawn_object(world, world_coords, "radio_feldfu_b", False)

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = main_turret
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("radio_operator", z)
    role.is_gunner = True
    role.turret = mg_turret
    role.is_radio_operator = True
    role.radio = z.ai.radio
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
    z.bounding_circles.append([[0.0, 0.0], 45])
    z.bounding_circles.append([[-43.0, -0.47619047619047616], 45])
    z.bounding_circles.append([[51.80952380952381, -0.09523809523809534], 45])
    z.bounding_circles.append([[-80.47619047619047, -37.61904761904762], 10])
    z.bounding_circles.append([[-80.47619047619047, 35.238095238095234], 10])
    z.bounding_circles.append([[81.9047619047619, -37.14285714285714], 10])
    z.bounding_circles.append([[82.85714285714285, 33.33333333333333], 10])
    z.weight = 26500
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
    z.ai.ammo_rack_capacity = 75
    for b in range(50):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "8.8cm_pak43_l71_magazine", False)
        )
    for b in range(25):
        temp = engine.world_builder.spawn_object(world, world_coords, "8.8cm_pak43_l71_magazine", False)
        engine.world_builder.load_magazine(world, temp, "Sprgr_34_88_L71")
        z.ai.ammo_rack.append(temp)
    z.ai.min_wheels_per_side_front = 3
    z.ai.min_wheels_per_side_rear = 3
    z.ai.max_wheels = 16
    z.ai.max_spare_wheels = 0
    for b in range(4):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
        z.ai.rear_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
        z.ai.rear_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
    return z
