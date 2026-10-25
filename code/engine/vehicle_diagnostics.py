"""
repo : https://github.com/openmarmot/twe

notes :
"""

import copy

import engine.math_2d


class VehicleDiagnostics:
    def __init__(self):
        self.vehicle = None
        self.screen_center = None

        # array of VehicleDiagnosticObject
        self.image_objects = []

        # tells graphic_engine to switch mode back to tactical
        self.exit = False

        # [['test,[0,0]],]
        self.text_queue = []

        self.text_black = "#000000"
        self.text_red = "#FF2121"

        self.menu_string = (
            "[Esc to Exit]  [1 Main]  [2 Turrets]  [3 Crew]  [4 Engine]  [5 Wheels]"
        )
        self.max_display_hits = 10

    # ---------------------------------------------------------------------------
    def handle_keydown(self, translated_key):

        if translated_key == "esc":
            self.exit = True
            return
        if translated_key == "1":
            self.load_main_screen()
        if translated_key == "2":
            self.load_turret_screen()
        if translated_key == "3":
            self.load_crew_screen()
        if translated_key == "4":
            self.load_engine_screen()
        if translated_key == "5":
            self.load_wheels_screen()

    # ---------------------------------------------------------------------------
    def load(self, vehicle, screen_center):
        self.vehicle = vehicle
        self.screen_center = screen_center
        self.load_main_screen()

    # ---------------------------------------------------------------------------
    def load_crew_screen(self):
        """load main screen text and image"""

        self.image_objects = []
        # add the main object
        v = VehicleDiagnosticObject()
        v.image_list = self.vehicle.image_list
        v.world_coords = copy.copy(self.vehicle.world_coords)
        self.image_objects.append(v)

        self.text_queue = []
        spacing = 15
        coord = [40, 15]

        self.text_queue.append([self.menu_string, copy.copy(coord), self.text_black])
        coord[1] += spacing
        coord[1] += spacing

        coord = [40, 100]
        self.text_queue.append(
            [
                "crew role | crew member (blood pressure) | current task",
                copy.copy(coord),
                self.text_black,
            ]
        )
        coord[1] += spacing
        for role in self.vehicle.ai.vehicle_crew:
            text = f"{role.role_name}: "
            if role.role_occupied:
                text += f"{role.human.name} ({role.human.ai.blood_pressure})"
                text += (
                    f": {role.human.ai.memory['task_vehicle_crew']['current_action']}"
                )
            else:
                text += "unoccupied"
            self.text_queue.append([text, copy.copy(coord), self.text_black])
            coord[1] += spacing

    # ---------------------------------------------------------------------------
    def queue_line(self, coord, spacing, text, color=None):
        """append one diagnostics line and advance the y coordinate"""
        if color is None:
            color = self.text_black
        self.text_queue.append([text, copy.copy(coord), color])
        coord[1] += spacing

    # ---------------------------------------------------------------------------
    def load_engine_screen(self):
        """load engine screen text and image"""

        self.image_objects = []
        # add the main object
        v = VehicleDiagnosticObject()
        v.image_list = self.vehicle.image_list
        v.screen_coords = self.screen_center
        self.image_objects.append(v)

        self.text_queue = []
        spacing = 15
        coord = [40, 15]
        ai = self.vehicle.ai

        self.queue_line(coord, spacing, self.menu_string)
        coord[1] += spacing

        # fuel and electrical sit in a second column when the window is wide
        # enough that the lines clear the vehicle sprite
        if self.screen_center[0] >= 520:
            side = [self.screen_center[0] + 180, coord[1]]
        else:
            side = None

        # - drivetrain -
        # drive force matches ai_vehicle.update_physics: each running engine
        # contributes max_engine_force * throttle_control, then that sum is
        # multiplied by the vehicle throttle again
        total_engine_force = 0.0
        for eng in ai.engines:
            if eng.ai.engine_on and eng.ai.damaged is False:
                total_engine_force += (
                    eng.ai.max_engine_force * eng.ai.throttle_control
                )
        drive_force = total_engine_force * ai.throttle

        if ai.engine_at_front:
            mount = "front"
        else:
            mount = "rear"
        gear_ratio = ai.transmission.get(ai.current_gear, ["?"])[0]

        self.queue_line(coord, spacing, "-- drivetrain --")
        self.queue_line(
            coord,
            spacing,
            f"engines on: {ai.engines_on}   engine mount: {mount}",
        )
        self.queue_line(
            coord,
            spacing,
            f"throttle: {ai.throttle:.2f}   returns to zero: {ai.throttle_zero}",
        )
        self.queue_line(
            coord,
            spacing,
            (
                f"brake: {ai.brake_power:.2f}   strength: {ai.brake_strength}"
                f"   returns to zero: {ai.brake_zero}"
            ),
        )
        self.queue_line(
            coord,
            spacing,
            (
                f"steering: {ai.wheel_steering:.2f}"
                f"   hull rotation: {ai.rotation_speed}"
            ),
        )
        self.queue_line(coord, spacing, f"gear: {ai.current_gear} ({gear_ratio})")
        self.queue_line(
            coord,
            spacing,
            (
                f"speed: {ai.current_speed:.1f}"
                f"   acceleration: {ai.acceleration:.2f}"
            ),
        )
        self.queue_line(
            coord,
            spacing,
            (
                f"max road: {ai.max_speed:.1f}   offroad: {ai.max_offroad_speed:.1f}"
                f"   dynamic: {ai.max_dynamic_speed:.1f}"
            ),
        )
        self.queue_line(
            coord,
            spacing,
            f"rolling resistance: {ai.rolling_resistance_coeff:.3f}",
        )
        self.queue_line(
            coord,
            spacing,
            (
                f"weight: {self.vehicle.weight} kg"
                f"   drag: {self.vehicle.drag_coefficient}"
                f"   frontal area: {self.vehicle.frontal_area}"
            ),
        )
        self.queue_line(
            coord,
            spacing,
            (
                f"engine force: {total_engine_force:.0f} N"
                f"   drive force: {drive_force:.0f} N"
            ),
        )
        leak_color = self.text_black
        if ai.fuel_leak:
            leak_color = self.text_red
        self.queue_line(coord, spacing, f"fuel leak: {ai.fuel_leak}", leak_color)
        disabled_color = self.text_black
        if ai.vehicle_disabled:
            disabled_color = self.text_red
        self.queue_line(
            coord, spacing, f"disabled: {ai.vehicle_disabled}", disabled_color
        )

        # - engines -
        coord[1] += spacing
        self.queue_line(coord, spacing, "-- engines --")
        if len(ai.engines) == 0:
            self.queue_line(coord, spacing, "no engines")
        for b in ai.engines:
            if b.ai.engine_on and b.ai.damaged is False:
                output_force = b.ai.max_engine_force * b.ai.throttle_control
            else:
                output_force = 0.0
            # max_engine_force = (horsepower * 745.7) / 0.7375
            horsepower = b.ai.max_engine_force * 0.7375 / 745.7
            if b.ai.fuel_type:
                fuels = ", ".join(b.ai.fuel_type)
            else:
                fuels = "none"
            loaded_per_min = b.ai.fuel_consumption_rate * 60
            idle_per_min = b.ai.idle_fuel_consumption_rate * 60

            self.queue_line(coord, spacing, b.name)
            on_color = self.text_black
            if b.ai.damaged:
                on_color = self.text_red
            self.queue_line(
                coord,
                spacing,
                (
                    f"-> on: {b.ai.engine_on}   damaged: {b.ai.damaged}"
                    f"   combustion: {b.ai.internal_combustion}"
                ),
                on_color,
            )
            self.queue_line(coord, spacing, f"-> fuel: {fuels}")
            self.queue_line(
                coord,
                spacing,
                (
                    f"-> burn: {b.ai.fuel_consumption_rate:.4f} L/s"
                    f" ({loaded_per_min:.2f} L/min)"
                    f"   idle: {b.ai.idle_fuel_consumption_rate:.4f} L/s"
                    f" ({idle_per_min:.2f} L/min)"
                ),
            )
            self.queue_line(
                coord,
                spacing,
                (
                    f"-> reservoir: {b.ai.fuel_reservoir:.3f} L"
                    f"   pending: {b.ai.fuel_consumed:.3f} L"
                ),
            )
            self.queue_line(
                coord,
                spacing,
                (
                    f"-> throttle control: {b.ai.throttle_control:.2f}"
                    f"   output: {output_force:.0f} N"
                ),
            )
            self.queue_line(
                coord,
                spacing,
                (
                    f"-> max force: {b.ai.max_engine_force:.0f} N"
                    f"   ({horsepower:.0f} hp)   weight: {b.weight} kg"
                ),
            )
            self.queue_line(
                coord,
                spacing,
                f"-> exhaust offset: {b.ai.exhaust_position_offset}",
            )

        # - fuel -
        # narrow windows continue down the left column
        if side is None:
            coord[1] += spacing
            side = coord
        self.queue_line(side, spacing, "-- fuel --")
        current_volume, max_volume = ai.read_fuel_gauge()
        self.queue_line(
            side,
            spacing,
            f"total: {current_volume:.1f} / {max_volume:.1f} L",
        )
        if len(ai.fuel_tanks) == 0:
            self.queue_line(side, spacing, "no fuel tanks")
        for tank in ai.fuel_tanks:
            self.queue_line(side, spacing, f"Fuel Tank: {tank.name}")
            self.queue_line(side, spacing, f"-> capacity: {tank.volume} L")
            if len(tank.ai.inventory) == 0:
                self.queue_line(side, spacing, "-> contents: empty", self.text_red)
            else:
                for item in tank.ai.inventory:
                    if item.is_liquid:
                        self.queue_line(
                            side,
                            spacing,
                            f"-> {item.name}: {item.volume:.2f} L",
                        )
                    else:
                        self.queue_line(
                            side,
                            spacing,
                            f"-> {item.name} (not liquid)",
                            self.text_red,
                        )
            if tank.ai.punctured:
                self.queue_line(
                    side,
                    spacing,
                    f"-> punctured   integrity: {tank.ai.container_integrity:.2f}",
                    self.text_red,
                )
            else:
                self.queue_line(
                    side,
                    spacing,
                    f"-> integrity: {tank.ai.container_integrity:.2f}",
                )
            if tank.ai.contaminated:
                self.queue_line(side, spacing, "-> contaminated", self.text_red)
            self.queue_line(side, spacing, f"-> self sealing: {tank.ai.self_sealing}")
            # update_fuel_system only drinks inventory[0], and only when the
            # name is in the engine fuel_type list
            if len(tank.ai.inventory) > 0:
                first = tank.ai.inventory[0]
                for eng in ai.engines:
                    rejects = (
                        first.is_liquid is False
                        or first.name not in eng.ai.fuel_type
                    )
                    if rejects:
                        self.queue_line(
                            side,
                            spacing,
                            f"-> {eng.name} rejects {first.name}",
                            self.text_red,
                        )

        # - electrical -
        # engines charge the batteries, and an internal-combustion start
        # requires a functioning electrical system
        side[1] += spacing
        self.queue_line(side, spacing, "-- electrical --")
        electrical_color = self.text_black
        if ai.electrical_system_functioning is False:
            electrical_color = self.text_red
        self.queue_line(
            side,
            spacing,
            f"electrical system: {ai.electrical_system_functioning}",
            electrical_color,
        )
        self.queue_line(side, spacing, f"alternator: {ai.alternator_amps} A")
        if len(ai.batteries) == 0:
            self.queue_line(side, spacing, "no batteries")
        for battery in ai.batteries:
            charge_color = self.text_black
            if battery.ai.state_of_charge <= 0:
                charge_color = self.text_red
            self.queue_line(
                side,
                spacing,
                (
                    f"{battery.name}: {battery.ai.state_of_charge:.1f}"
                    f"/{battery.ai.max_capacity:.0f} Ah"
                    f"   {battery.ai.voltage} V {battery.ai.type}"
                    f"   health {battery.ai.health:.2f}"
                ),
                charge_color,
            )

    # ---------------------------------------------------------------------------
    def load_main_screen(self):
        """load main screen text and image"""

        self.image_objects = []
        # add the main object
        v = VehicleDiagnosticObject()
        v.image_list = self.vehicle.image_list
        v.screen_coords = self.screen_center
        self.image_objects.append(v)

        # load collision markers
        for hit in self.vehicle.ai.collision_log:
            v = VehicleDiagnosticObject()
            if hit.penetrated:
                v.image_list = ["hit_orange"]
            else:
                v.image_list = ["hit_green"]
            v.rotation_angle = engine.math_2d.get_normalized_angle(hit.rotation_offset)
            v.world_coords = engine.math_2d.calculate_relative_position(
                self.vehicle.world_coords, 0, hit.position_offset
            )
            self.image_objects.append(v)

        self.text_queue = []
        spacing = 15
        coord = [40, 15]

        self.text_queue.append([self.menu_string, copy.copy(coord), self.text_black])
        coord[1] += spacing
        coord[1] += spacing

        self.text_queue.append(
            [f"vehicle: {self.vehicle.name}", copy.copy(coord), self.text_black]
        )
        coord[1] += spacing
        if self.vehicle.ai.vehicle_disabled:
            self.text_queue.append(["disabled", copy.copy(coord), self.text_red])
            coord[1] += spacing

        # armor
        coord = [40, 150]
        self.text_queue.append(["-- armor --", copy.copy(coord), self.text_black])
        coord[1] += spacing
        self.text_queue.append(
            ["[armor, slope, spaced armor]", copy.copy(coord), self.text_black]
        )
        coord[1] += spacing
        self.text_queue.append(
            ["vehicle body armor", copy.copy(coord), self.text_black]
        )
        coord[1] += spacing
        for key, value in self.vehicle.ai.vehicle_armor.items():
            self.text_queue.append(
                [f"{key} : {value}", copy.copy(coord), self.text_black]
            )
            coord[1] += spacing
        self.text_queue.append(
            ["passenger compartment armor", copy.copy(coord), self.text_black]
        )
        coord[1] += spacing
        for key, value in self.vehicle.ai.passenger_compartment_armor.items():
            self.text_queue.append(
                [f"{key} : {value}", copy.copy(coord), self.text_black]
            )
            coord[1] += spacing

        # diagnostics
        coord = [40, 450]
        self.text_queue.append(["-- diagnostics --", copy.copy(coord), self.text_black])
        coord[1] += spacing
        for b in self.vehicle.ai.turrets:
            if b.ai.turret_jammed:
                self.text_queue.append(
                    [f"{b.name} jammed", copy.copy(coord), self.text_red]
                )
                coord[1] += spacing
            if b.ai.primary_weapon.ai.damaged:
                self.text_queue.append(
                    [
                        f"{b.ai.primary_weapon.name} damaged",
                        copy.copy(coord),
                        self.text_red,
                    ]
                )
                coord[1] += spacing

        wheel_damage = False
        wheel_destroyed = False
        for b in self.vehicle.ai.front_left_wheels:
            if b.ai.damaged:
                wheel_damage = True
            if b.ai.destroyed:
                wheel_destroyed = True
        for b in self.vehicle.ai.front_right_wheels:
            if b.ai.damaged:
                wheel_damage = True
            if b.ai.destroyed:
                wheel_destroyed = True
        for b in self.vehicle.ai.rear_left_wheels:
            if b.ai.damaged:
                wheel_damage = True
            if b.ai.destroyed:
                wheel_destroyed = True
        for b in self.vehicle.ai.rear_right_wheels:
            if b.ai.damaged:
                wheel_damage = True
            if b.ai.destroyed:
                wheel_destroyed = True
        if wheel_damage:
            self.text_queue.append(
                ["wheel(s) damaged", copy.copy(coord), self.text_red]
            )
            coord[1] += spacing
        if wheel_destroyed:
            self.text_queue.append(
                ["wheel(s) destroyed", copy.copy(coord), self.text_red]
            )
            coord[1] += spacing
        engine_damaged = False
        for b in self.vehicle.ai.engines:
            if b.ai.damaged:
                engine_damaged = True
        if engine_damaged:
            self.text_queue.append(
                ["engine(s) damaged", copy.copy(coord), self.text_red]
            )
            coord[1] += spacing

        # - fuel tank data -
        # this should move to its own page

        coord = [40, 600]
        self.text_queue.append(["-- fuel data --", copy.copy(coord), self.text_black])
        coord[1] += spacing
        for b in self.vehicle.ai.fuel_tanks:
            self.text_queue.append(
                [f"Fuel Tank: {b.name}", copy.copy(coord), self.text_black]
            )
            coord[1] += spacing
            if len(b.ai.inventory) > 0:
                if "gas" in b.ai.inventory[0].name:
                    self.text_queue.append(
                        [
                            f"-> gas: {b.ai.inventory[0].volume} liters",
                            copy.copy(coord),
                            self.text_black,
                        ]
                    )
                    coord[1] += spacing
                if "diesel" in b.ai.inventory[0].name:
                    self.text_queue.append(
                        [
                            f"-> diesel: {b.ai.inventory[0].volume} liters",
                            copy.copy(coord),
                            self.text_black,
                        ]
                    )
                    coord[1] += spacing
            if b.ai.punctured:
                self.text_queue.append(
                    [f"-> punctured", copy.copy(coord), self.text_red]
                )
                coord[1] += spacing
            if b.ai.contaminated:
                self.text_queue.append(
                    [f"-> contaminated", copy.copy(coord), self.text_red]
                )
                coord[1] += spacing

        # - hit log data -
        coord = [40, 700]
        self.text_queue.append(
            ["-- recent hit data --", copy.copy(coord), self.text_black]
        )
        coord[1] += spacing

        total_penetrated = len(
            [h for h in self.vehicle.ai.collision_log if h.penetrated]
        )
        total_non_penetrated = len(
            [h for h in self.vehicle.ai.collision_log if not h.penetrated]
        )
        self.text_queue.append(
            [
                f"Total hits - Penetrated: {total_penetrated}, Non-penetrated: {total_non_penetrated}",
                copy.copy(coord),
                self.text_black,
            ]
        )
        coord[1] += spacing

        penetrated_sorted = sorted(
            [h for h in self.vehicle.ai.collision_log if h.penetrated],
            key=lambda x: x.penetration_value,
            reverse=True,
        )
        non_penetrated_sorted = sorted(
            [h for h in self.vehicle.ai.collision_log if not h.penetrated],
            key=lambda x: x.penetration_value,
            reverse=True,
        )

        hits_to_show = []
        hits_to_show.extend(penetrated_sorted[: self.max_display_hits])
        remaining_slots = self.max_display_hits - len(hits_to_show)
        if remaining_slots > 0 and non_penetrated_sorted:
            hits_to_show.extend(non_penetrated_sorted[:remaining_slots])

        for b in hits_to_show:
            pen_text = f"[penetrated: {b.penetrated}] [distance: {b.distance}] [projectile: {b.projectile_name}] [penetration value: {b.penetration_value}] [armor value: {b.armor_value}] [side: {b.hit_side}] [compartment: {b.hit_compartment}] [result: {b.result}]"
            if b.penetrated:
                self.text_queue.append([pen_text, copy.copy(coord), self.text_red])
                coord[1] += spacing
            else:
                self.text_queue.append([pen_text, copy.copy(coord), self.text_black])
                coord[1] += spacing

    # ---------------------------------------------------------------------------
    def get_turret_ammo_types(self, weapon, vehicle):
        """get a dict of projectile types and counts for all compatible magazines"""
        ammo_types = {}

        # check magazines in inventory
        for b in vehicle.ai.inventory:
            if b.is_gun_magazine:
                if weapon.world_builder_identity in b.ai.compatible_guns:
                    for projectile in b.ai.projectiles:
                        p_type = projectile.ai.projectile_type
                        if p_type in ammo_types:
                            ammo_types[p_type] += 1
                        else:
                            ammo_types[p_type] = 1

        # check ammo_rack for vehicles
        if vehicle.is_vehicle:
            for b in vehicle.ai.ammo_rack:
                if b.is_gun_magazine:
                    if weapon.world_builder_identity in b.ai.compatible_guns:
                        for projectile in b.ai.projectiles:
                            p_type = projectile.ai.projectile_type
                            if p_type in ammo_types:
                                ammo_types[p_type] += 1
                            else:
                                ammo_types[p_type] = 1

        return ammo_types

    # ---------------------------------------------------------------------------
    def load_turret_screen(self):
        """load main screen text and image"""

        self.image_objects = []
        turret_coords = []
        if len(self.vehicle.ai.turrets) == 0:
            pass
        elif len(self.vehicle.ai.turrets) == 1:
            turret_coords = [self.screen_center]
        if len(self.vehicle.ai.turrets) == 2:
            turret_coords = []
            turret_coords.append([self.screen_center[0] + 200, self.screen_center[1]])
            turret_coords.append([self.screen_center[0] - 200, self.screen_center[1]])

        if len(self.vehicle.ai.turrets) == 3:
            turret_coords = []
            turret_coords.append([self.screen_center[0] + 200, self.screen_center[1]])
            turret_coords.append([self.screen_center[0], self.screen_center[1]])
            turret_coords.append([self.screen_center[0] - 300, self.screen_center[1]])

        for turret in self.vehicle.ai.turrets:
            v = VehicleDiagnosticObject()
            v.image_list = turret.image_list
            v.screen_coords = turret_coords.pop()
            self.image_objects.append(v)

        self.text_queue = []
        spacing = 15
        coord = [40, 15]

        self.text_queue.append([self.menu_string, copy.copy(coord), self.text_black])
        coord[1] += spacing
        coord[1] += spacing

        # - turret data -
        # this should eventually move to its own page
        coord = [40, 150]

        for b in self.vehicle.ai.turrets:
            self.text_queue.append(
                [f"Turret: {b.name}", copy.copy(coord), self.text_black]
            )
            coord[1] += spacing

            if b.ai.turret_jammed:
                self.text_queue.append(
                    [" -> Turret ring is jammed", copy.copy(coord), self.text_red]
                )
                coord[1] += spacing

            if b.ai.primary_weapon != None:
                self.text_queue.append(
                    [
                        f" -> {b.ai.primary_weapon.name}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing
                if b.ai.primary_weapon.ai.action_jammed:
                    self.text_queue.append(
                        [" --> action is jammed", copy.copy(coord), self.text_red]
                    )
                    coord[1] += spacing
                if b.ai.primary_weapon.ai.damaged:
                    self.text_queue.append(
                        [" --> weapon is damaged", copy.copy(coord), self.text_red]
                    )
                    coord[1] += spacing
                ammo_gun, ammo_inventory, magazine_count = (
                    self.vehicle.world.player.ai.check_ammo(
                        b.ai.primary_weapon, self.vehicle
                    )
                )
                self.text_queue.append(
                    [
                        f" --> ammo {ammo_gun}/{ammo_inventory}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing
                self.text_queue.append(
                    [
                        f" --> rounds fired: {b.ai.primary_weapon.ai.rounds_fired}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing

                # display rounds fired by type
                fired_types = getattr(b.ai.primary_weapon.ai, "rounds_fired_type", {})
                if fired_types:
                    self.text_queue.append(
                        [" --> rounds fired by type:", copy.copy(coord), self.text_black]
                    )
                    coord[1] += spacing
                    for p_type, count in fired_types.items():
                        self.text_queue.append(
                            [
                                f"     {p_type}: {count}",
                                copy.copy(coord),
                                self.text_black,
                            ]
                        )
                        coord[1] += spacing

                self.text_queue.append(
                    [
                        f" --> accuracy: {b.ai.primary_weapon.ai.get_accuracy()}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing

                # display ammo types breakdown
                ammo_types = self.get_turret_ammo_types(
                    b.ai.primary_weapon, self.vehicle
                )
                if ammo_types:
                    self.text_queue.append(
                        [" --> ammo types:", copy.copy(coord), self.text_black]
                    )
                    coord[1] += spacing
                    for p_type, count in ammo_types.items():
                        self.text_queue.append(
                            [
                                f"     {p_type}: {count}",
                                copy.copy(coord),
                                self.text_black,
                            ]
                        )
                        coord[1] += spacing

            if b.ai.coaxial_weapon != None:
                self.text_queue.append(
                    [
                        f" -> {b.ai.coaxial_weapon.name}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing
                if b.ai.coaxial_weapon.ai.action_jammed:
                    self.text_queue.append(
                        [" --> action is jammed", copy.copy(coord), self.text_red]
                    )
                    coord[1] += spacing
                if b.ai.coaxial_weapon.ai.damaged:
                    self.text_queue.append(
                        [" --> weapon is damaged", copy.copy(coord), self.text_red]
                    )
                    coord[1] += spacing
                ammo_gun, ammo_inventory, magazine_count = (
                    self.vehicle.world.player.ai.check_ammo(
                        b.ai.coaxial_weapon, self.vehicle
                    )
                )
                self.text_queue.append(
                    [
                        f" --> ammo {ammo_gun}/{ammo_inventory}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing
                self.text_queue.append(
                    [
                        f" --> rounds fired: {b.ai.coaxial_weapon.ai.rounds_fired}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing

                # display rounds fired by type
                fired_types = getattr(b.ai.coaxial_weapon.ai, "rounds_fired_type", {})
                if fired_types:
                    self.text_queue.append(
                        [" --> rounds fired by type:", copy.copy(coord), self.text_black]
                    )
                    coord[1] += spacing
                    for p_type, count in fired_types.items():
                        self.text_queue.append(
                            [
                                f"     {p_type}: {count}",
                                copy.copy(coord),
                                self.text_black,
                            ]
                        )
                        coord[1] += spacing

                self.text_queue.append(
                    [
                        f" --> accuracy: {b.ai.coaxial_weapon.ai.get_accuracy()}",
                        copy.copy(coord),
                        self.text_black,
                    ]
                )
                coord[1] += spacing

                # display ammo types breakdown
                ammo_types = self.get_turret_ammo_types(
                    b.ai.coaxial_weapon, self.vehicle
                )
                if ammo_types:
                    self.text_queue.append(
                        [" --> ammo types:", copy.copy(coord), self.text_black]
                    )
                    coord[1] += spacing
                    for p_type, count in ammo_types.items():
                        self.text_queue.append(
                            [
                                f"     {p_type}: {count}",
                                copy.copy(coord),
                                self.text_black,
                            ]
                        )
                        coord[1] += spacing

            coord[1] += spacing
            coord[1] += spacing

    # ---------------------------------------------------------------------------
    def load_wheels_screen(self):
        """load main screen text and image"""

        self.image_objects = []
        # add the main object
        v = VehicleDiagnosticObject()
        v.image_list = self.vehicle.image_list
        v.screen_coords = self.screen_center
        self.image_objects.append(v)

        self.text_queue = []
        spacing = 15
        coord = [40, 15]

        self.text_queue.append([self.menu_string, copy.copy(coord), self.text_black])
        coord[1] += spacing
        coord[1] += spacing

    # ---------------------------------------------------------------------------
    def update(self):
        """update. called by graphics_2d_pygame"""

        pass


class VehicleDiagnosticObject:
    def __init__(self):
        self.screen_coords = [0, 0]
        self.world_coords = [0, 0]
        self.scale_modifier = 0
        self.image = None
        self.image_index = 0
        self.image_list = []
        self.image_size = None
        self.rotation_angle = 0
        self.reset_image = True
