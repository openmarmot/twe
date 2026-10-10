"""
repo : https://github.com/openmarmot/twe

notes : the turret for a tank, or the mg mount on a vehicle
"""

# import built in modules
import copy
import random

# import custom packages
import engine.math_2d
import engine.log
import engine.penetration_calculator
import engine.world_builder

# global variables


class AITurret:
    """turret for a tank, or the mg mount on a vehicle"""

    def __init__(self, owner):
        self.owner = owner

        # [side][armor thickness,armor slope,spaced_armor_thickness]
        # slope 0 degrees is vertical, 90 degrees is horizontal
        # armor grade steel thickness in mm. standard soft aluminum/steel is a 0-1
        self.turret_armor = {}
        self.turret_armor["top"] = [0, 0, 0]
        self.turret_armor["bottom"] = [0, 0, 0]
        self.turret_armor["left"] = [0, 0, 0]
        self.turret_armor["right"] = [0, 0, 0]
        self.turret_armor["front"] = [0, 0, 0]
        self.turret_armor["rear"] = [0, 0, 0]

        # the side of the vehicle the turret is mounted on top/bottom/left/right/front/rear
        # most turrets should be mounted on the top
        self.vehicle_mount_side = "top"

        # turret accuracy. 0 is perfect accuracy
        # basically a measure of how easy/hard it is to aim
        self.turret_accuracy = 0

        # this means that it can no longer rotate
        self.turret_jammed = False

        # for remote operated machine guns - mostly german
        self.remote_operated = False

        # offset to position it correctly on a vehicle. vehicle specific
        self.position_offset = [0, 0]

        # this is relative to the vehicle
        # really + or - a certain amount of degrees
        self.turret_rotation = 0

        # gunner requested rotation change
        self.rotation_change = 0

        # rotation range for the turret
        # full rotation is [-360,360]
        self.rotation_range = [-20, 20]

        # degrees per second at a full traverse command.
        # turret definitions override this.
        self.rotation_speed = 20

        self.vehicle = None
        self.last_vehicle_position = [0, 0]
        self.last_vehicle_rotation = 0

        # very important!
        # whether this is the main/most important turret or not.
        # used by ai_human to determine actions
        self.primary_turret = False

        # note - extra magazines/ammo should be stored in the vehicle inventory
        self.primary_weapon = None
        self.coaxial_weapon = None

        # these are here because reload speed is heavily affected by turret design
        self.primary_weapon_reload_speed = 0
        self.coaxial_weapon_reload_speed = 0

        # turrets with the small attribute are less likely to be hit
        self.small = False

        self.gun_sight = None

    # ---------------------------------------------------------------------------
    def calculate_accuracy(self, weapon):
        """calculate mechanical accuracy."""

        # note most accuracy calculation should be done in ai_human_vehicle_gunner.calculate_turret_aim
        # this is smaller variations that get added when the bullet is fired

        temp_heading = engine.math_2d.get_heading_from_rotation(
            self.owner.rotation_angle
        )
        far_coords = engine.math_2d.moveAlongVector(
            1000, self.owner.world_coords, temp_heading, 1
        )

        adjust_max = 0
        adjust_max += weapon.ai.mechanical_accuracy
        adjust_max += self.turret_accuracy

        if self.vehicle.ai.current_speed > 0:
            adjust_max += 20
        if self.vehicle.ai.current_speed > 100:
            adjust_max += 30

        # apply adjustment
        far_coords = [
            far_coords[0] + random.uniform(-adjust_max, adjust_max),
            far_coords[1] + random.uniform(-adjust_max, adjust_max),
        ]

        # get the new angle
        return engine.math_2d.get_rotation(self.owner.world_coords, far_coords)

    # ---------------------------------------------------------------------------
    def event_collision(self, event_data):
        """handle collision events for the turret"""

        if event_data.is_projectile:
            projectile = event_data
            distance = engine.math_2d.get_distance(
                self.owner.world_coords, projectile.ai.starting_coords
            )

            half_length, half_width = engine.math_2d.get_collision_half_extents(
                self.owner
            )
            side, relative_angle = engine.math_2d.calculate_hit_side(
                self.owner.rotation_angle,
                projectile.rotation_angle,
                self.owner.world_coords,
                projectile.world_coords,
                half_length,
                half_width,
            )
            penetration, pen_value, armor_value, spaced_effect = (
                engine.penetration_calculator.calculate_penetration(
                    projectile,
                    distance,
                    "steel",
                    self.turret_armor[side],
                    side,
                    relative_angle,
                )
            )
            result = ""
            if spaced_effect == "destabilized":
                result = "destabilized by spaced armor"

            into_hull = False
            burst_already = False
            if penetration:
                result, into_hull, burst_already = self.handle_penetration(
                    projectile, side, pen_value, armor_value, result
                )
            else:
                result = self.handle_non_penetration(
                    projectile, side, pen_value, armor_value, spaced_effect, result
                )

            if self.vehicle is not None:
                self.vehicle.ai.add_hit_data(
                    projectile,
                    penetration,
                    side,
                    distance,
                    f"Turret {self.owner.name}",
                    result,
                    pen_value,
                    armor_value,
                )
            # hull line follows the turret line. a burst already logged above does not repeat.
            if into_hull and self.vehicle is not None:
                self.vehicle.ai.projectile_hit_vehicle_body(
                    projectile, side, relative_angle, burst_already=burst_already
                )
            elif penetration:
                projectile.wo_stop()

        elif event_data.is_grenade:
            print("bonk")
        else:
            engine.log.add_data(
                "error",
                "ai_vehicle event_collision - unhandled collision type"
                + event_data.name,
                True,
            )

    # ---------------------------------------------------------------------------
    def handle_event(self, event, event_data):
        """overrides base handle_event"""
        # EVENT - text describing event
        # event_data - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if event == "add_inventory":
            engine.log.add_data(
                "Error", "ai_turret handle_event add_inventory not implemented", True
            )
            # self.event_add_inventory(event_data)
        elif event == "collision":
            self.event_collision(event_data)
        elif event == "remove_inventory":
            engine.log.add_data(
                "Error", "ai_turret handle_event remove_inventory not implemented", True
            )
            # self.event_remove_inventory(event_data)
        else:
            print("Error: " + self.owner.name + " cannot handle event " + event)

    # ---------------------------------------------------------------------------
    def strike_turret_crew(self, projectile):
        """one pass of a projectile through the crew serving this turret.

        Each occupied crewman is hit at 50%. Remote mounts have no crew in the
        fragment path. Returns True when somebody was hit.
        """
        if self.vehicle is None or self.remote_operated:
            return False
        struck = False
        for role in self.vehicle.ai.vehicle_crew:
            if role.role_occupied and role.turret == self.owner:
                if random.randint(0, 1) == 1:
                    role.human.ai.handle_event("collision", projectile)
                    struck = True
        return struck

    # ---------------------------------------------------------------------------
    def handle_spalling_damage(self, projectile, attempts=None, keep_all=False):
        """throw armor fragments at the crew serving this turret.

        attempts None is the near-miss roll: 1-3 tries, one in three kept.
        A perforation passes an attempt count and keep_all, because the plug
        is already inside. Returns how many fragments were spawned.
        """
        if attempts is None:
            attempts = random.randint(1, 3)
            keep_all = False

        spawned = 0
        for _ in range(attempts):
            if keep_all or random.randint(0, 2) == 0:
                shrapnel = engine.world_builder.spawn_object(
                    self.owner.world, self.owner.world_coords, "projectile", False
                )
                shrapnel.ai.projectile_type = "shrapnel"
                shrapnel.name = "shrapnel"
                shrapnel.ai.starting_coords = copy.copy(self.owner.world_coords)
                shrapnel.ai.shooter = projectile.ai.shooter
                shrapnel.ai.weapon = projectile.ai.weapon

                if self.remote_operated is False and self.vehicle is not None:
                    for role in self.vehicle.ai.vehicle_crew:
                        if role.role_occupied and role.turret == self.owner:
                            if random.randint(0, 1) == 1:
                                role.human.ai.handle_event("collision", shrapnel)
                spawned += 1
        return spawned

    # ---------------------------------------------------------------------------
    def handle_rotate_left(self):
        """handle left rotation input"""
        if self.turret_jammed is False:
            self.rotation_change = 1

    # ---------------------------------------------------------------------------
    def handle_rotate_right(self):
        """handle right rotation input"""
        if self.turret_jammed is False:
            self.rotation_change = -1

    # ---------------------------------------------------------------------------
    def handle_fire(self):
        """fire the primary weapon"""
        if self.primary_weapon.ai.check_if_can_fire():
            self.primary_weapon.rotation_angle = self.calculate_accuracy(
                self.primary_weapon
            )
            self.primary_weapon.ai.fire()
            self.vehicle.ai.recent_noise_or_move = True
            self.vehicle.ai.recent_noise_or_move_time = self.owner.world.world_seconds
            return True
        return False

    # ---------------------------------------------------------------------------
    def handle_fire_coax(self):
        """fire the coaxial weapon"""
        if self.coaxial_weapon.ai.check_if_can_fire():
            self.coaxial_weapon.rotation_angle = self.calculate_accuracy(
                self.coaxial_weapon
            )
            self.coaxial_weapon.ai.fire()
            self.vehicle.ai.recent_noise_or_move = True
            self.vehicle.ai.recent_noise_or_move_time = self.owner.world.world_seconds
            return True
        return False

    # ---------------------------------------------------------------------------
    def handle_penetration(self, projectile, side, pen_value, armor_value, result):
        """handle projectile penetration of turret armor.

        The crew in this turret are hit by the penetrator, or by the shell
        burst if it is APHE. Hardware damage is additional. A large overmatch
        can continue down into the hull. Returns (result, into_hull, burst_already).
        The caller logs this hit before applying the hull follow-through.
        """
        thickness = self.turret_armor[side][0]
        diameter = engine.penetration_calculator.projectile_diameter(projectile)
        overmatch = engine.penetration_calculator.overmatch_ratio(pen_value, armor_value)
        internal = (
            thickness >= 1
            and self.remote_operated is False
            and engine.penetration_calculator.is_internal_burst(projectile)
        )
        join = engine.penetration_calculator.join_hit_result

        attempts = engine.penetration_calculator.perforation_fragment_attempts(
            thickness, diameter, pen_value, armor_value
        )
        if attempts > 0:
            count = self.handle_spalling_damage(projectile, attempts, True)
            result = join(result, f"spall x{count}")

        if thickness < 1:
            # no plate and no fuze. half the time the shot misses the crew entirely.
            if self.remote_operated or self.vehicle is None:
                result = join(result, "sailed through")
            elif random.randint(0, 1) == 0:
                result = join(result, "sailed through")
            elif self.strike_turret_crew(projectile):
                result = join(result, "crew")
            else:
                result = join(result, "crew missed")
        elif internal:
            struck = self.strike_turret_crew(projectile)
            struck = self.strike_turret_crew(projectile) or struck
            result = join(result, "internal burst")
            if struck is False:
                result = join(result, "crew missed")
        elif self.remote_operated or self.vehicle is None:
            pass
        elif self.strike_turret_crew(projectile):
            result = join(result, "crew")
        else:
            result = join(result, "crew missed")

        if diameter > 20 and self.primary_weapon:
            self.primary_weapon.ai.damaged = True
            if (
                self.primary_turret
                and self.vehicle is not None
                and self.vehicle.ai.is_transport is False
            ):
                self.vehicle.ai.vehicle_disabled = True
            result = join(result, "primary weapon")
        if diameter > 20 and self.coaxial_weapon:
            self.coaxial_weapon.ai.damaged = True
            result = join(result, "coaxial weapon")

        # a marginal perforation fouls the traverse. a gross overmatch punches a hole and moves on.
        if overmatch < 2 and random.randint(0, 1) == 0:
            self.turret_jammed = True
            if (
                self.primary_turret
                and self.vehicle is not None
                and self.vehicle.ai.is_transport is False
            ):
                self.vehicle.ai.vehicle_disabled = True
            result = join(result, "traverse jammed")

        if (
            self.vehicle is not None
            and self.remote_operated is False
            and self.vehicle.ai.roll_ammo_detonation(
                projectile, len(self.vehicle.ai.ammo_rack) > 0, internal
            )
        ):
            result = join(result, "ammo rack")

        into_hull = (
            overmatch >= 2
            and self.vehicle is not None
            and random.randint(0, 1) == 0
        )
        if into_hull:
            result = join(result, "continued into hull")

        if result == "":
            result = "penetration"
        return result, into_hull, internal

    # ---------------------------------------------------------------------------
    def handle_non_penetration(
        self, projectile, side, pen_value, armor_value, spaced_effect, result
    ):
        """handle projectile that does not penetrate turret armor"""

        thickness = self.turret_armor[side][0]
        diameter = engine.penetration_calculator.projectile_diameter(projectile)
        join = engine.penetration_calculator.join_hit_result
        # near the ballistic limit, thick plate can scab with the shot still outside
        if (
            pen_value >= armor_value * 0.9
            and spaced_effect != "destabilized"
            and engine.penetration_calculator.plate_throws_fragments(thickness, diameter)
        ):
            count = self.handle_spalling_damage(projectile)
            result = join(result, f"spalling x{count}")
        elif self.vehicle is not None:
            self.vehicle.ai.projectile_bounce(projectile)

        return result

    # ---------------------------------------------------------------------------
    def neutral_controls(self):
        """return controls to neutral over time"""

        if self.rotation_change != 0:
            # controls should return to neutral over time
            time_passed = self.owner.world.time_passed_seconds

            # return wheel to neutral
            self.rotation_change = engine.math_2d.regress_to_zero(
                self.rotation_change, time_passed
            )

    # ---------------------------------------------------------------------------
    def sync_to_vehicle(self):
        """attach turret to current vehicle position/rotation.

        Called by ai_vehicle.update_child_position_rotation so hull and turret
        share the same frame. Also used after turret yaw changes.
        """
        if self.vehicle is None:
            return

        new_angle = engine.math_2d.get_normalized_angle(
            self.vehicle.rotation_angle + self.turret_rotation
        )
        self.owner.world_coords = engine.math_2d.calculate_relative_position(
            self.vehicle.world_coords,
            self.vehicle.rotation_angle,
            self.position_offset,
        )
        # only rebuild sprite when facing actually changes (not every translate)
        if self.owner.rotation_angle != new_angle:
            self.owner.reset_image = True
        self.owner.rotation_angle = new_angle

        self.last_vehicle_position = copy.copy(self.vehicle.world_coords)
        self.last_vehicle_rotation = self.vehicle.rotation_angle

    # ---------------------------------------------------------------------------
    def update(self):
        """update the turret state"""

        self.update_physics()

        self.neutral_controls()

    # ---------------------------------------------------------------------------
    def update_physics(self):
        """update turret physics"""
        time_passed = self.owner.world.time_passed_seconds
        relative_rotation_changed = False

        if self.rotation_change != 0:
            relative_rotation_changed = True
            self.turret_rotation += (
                self.rotation_change * self.rotation_speed * time_passed
            )

            # Check if turret allows full 360-degree rotation
            if self.rotation_range == [-360, 360]:
                # Normalize rotation to stay within [0, 360) for continuous rotation
                self.turret_rotation = engine.math_2d.get_normalized_angle(
                    self.turret_rotation
                )
            else:
                # Enforce restricted rotation range without resetting rotation_change
                if self.turret_rotation < self.rotation_range[0]:
                    self.turret_rotation = self.rotation_range[0]
                elif self.turret_rotation > self.rotation_range[1]:
                    self.turret_rotation = self.rotation_range[1]

        if self.vehicle is None:
            return

        # vehicle movement is normally applied via update_child_position_rotation.
        # keep a fallback if this turret updates before the vehicle this frame,
        # or if something moved the hull without going through update_child.
        vehicle_moved = (
            self.last_vehicle_position != self.vehicle.world_coords
            or self.last_vehicle_rotation != self.vehicle.rotation_angle
        )

        if relative_rotation_changed or vehicle_moved:
            self.sync_to_vehicle()
            # crew seats relative to this turret need a refresh after yaw
            if relative_rotation_changed:
                self.vehicle.ai.update_child_position_rotation()