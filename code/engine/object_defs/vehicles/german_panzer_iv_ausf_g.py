"""
german_panzer_iv_ausf_g object definition

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


@register_object("german_panzer_iv_ausf_g")
def create(world, world_coords):
    # ref : https://wiki.warthunder.com/unit/germ_pzkpfw_IV_ausf_G
    z = WorldObject(
        world, ["panzer_iv_g_chassis", "panzer_iv_g_chassis_destroyed"], AIVehicle
    )
    z.name = "Panzer IV Ausf. G"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.requires_afv_training = True
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.vehicle_armor["top"] = [16, 0, 0]
    z.ai.vehicle_armor["bottom"] = [8, 0, 0]
    z.ai.vehicle_armor["left"] = [30, 0, 0]
    z.ai.vehicle_armor["right"] = [30, 0, 0]
    z.ai.vehicle_armor["front"] = [80, 64, 0]
    z.ai.vehicle_armor["rear"] = [30, 15, 0]
    z.ai.passenger_compartment_armor["top"] = [16, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [8, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [30, 0, 0]
    z.ai.passenger_compartment_armor["right"] = [30, 0, 0]
    z.ai.passenger_compartment_armor["front"] = [80, 11, 0]
    z.ai.passenger_compartment_armor["rear"] = [30, 15, 0]
    main_turret = engine.world_builder.spawn_object(world, world_coords, "panzer_iv_g_turret", True)
    z.ai.turrets.append(main_turret)
    main_turret.ai.vehicle = z
    mg_turret = engine.world_builder.spawn_object(world, world_coords, "panzer_iv_hull_mg", True)
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
    z.bounding_circles.append([[-48.0, 0.0], 40])
    z.bounding_circles.append([[-20.0, 0.0], 40])
    z.bounding_circles.append([[7.0, 0.0], 40])
    z.bounding_circles.append([[34.0, 0.0], 40])
    z.bounding_circles.append([[48.0, 0.0], 40])
    z.weight = 25000
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
    z.ai.ammo_rack_capacity = 87
    for b in range(60):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "75mm_kwk40_l43_magazine", False)
        )
    for b in range(27):
        temp = engine.world_builder.spawn_object(world, world_coords, "75mm_kwk40_l43_magazine", False)
        engine.world_builder.load_magazine(world, temp, "Sprgr_34_75_L43")
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
