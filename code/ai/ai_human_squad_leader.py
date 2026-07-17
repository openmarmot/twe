"""
repo : https://github.com/openmarmot/twe

notes : squad leader specific ai logic extracted from ai_human.py
"""

# import built in modules
import random
import copy

# import custom packages
import engine.math_2d
from engine.vehicle_order import VehicleOrder
from engine.tactical_order import TacticalOrder


class AIHumanSquadLeader:
    def __init__(self, owner):
        self.owner = owner

    # ---------------------------------------------------------------------------
    def review_orders(self):
        """review tactical orders return true if a action was taken"""

        # the distance that is considered close enough to have arrived at a target distance
        # this should be greater than the distance a vehicle driver stops at.
        close_distance = 300

        # note this can be called from inside a vehicle or from on foot

        # this is a list of TacticalOrder objects
        # for now i think its always only one
        orders = self.owner.ai.memory["task_squad_leader"]["orders"]

        if len(orders) == 0:
            self.tactical_decision()
            return False

        # i think we will just focus on the first one
        order = orders[0]

        if order.order_defend_area:
            distance = engine.math_2d.get_distance(
                self.owner.world_coords, order.world_coords
            )
            if distance > close_distance:
                # in a vehicle
                if self.owner.ai.in_vehicle():
                    vehicle_order = VehicleOrder()
                    vehicle_order.order_drive_to_coords = True
                    vehicle_order.world_coords = copy.copy(order.world_coords)
                    if self.owner.ai.memory["task_vehicle_crew"][
                        "vehicle_role"
                    ].vehicle.ai.is_transport:
                        vehicle_order.exit_vehicle_when_finished = True

                    # the driver will grab this when out of orders
                    self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = vehicle_order
                    return True
                # we must be on foot
                self.owner.ai.switch_task_move_to_location(order.world_coords, None)
                return True
            else:
                # we are in position - check if we should complete the defend order
                if order.world_area.is_contested:
                    # area is being contested - mark that it has been contested
                    order.was_contested = True
                elif order.was_contested:
                    # area WAS contested but no longer is - we won, order complete
                    orders.remove(order)
                # else: area has never been contested, keep defending

                # building awareness: seek closest building for cover when defending
                # or when there has been recent gunfire in this grid square
                building = self.owner.ai.closest_building
                if building is not None:
                    bdist = engine.math_2d.get_distance(
                        self.owner.world_coords, building.world_coords
                    )
                    cover_dist = building.collision_radius * 0.5
                    if bdist > cover_dist:
                        recent_fire = (
                            self.owner.grid_square.last_gun_fired + 30
                            > self.owner.world.world_seconds
                        )
                        if order.order_defend_area or recent_fire:
                            if not self.owner.ai.in_vehicle():
                                self.owner.ai.switch_task_move_to_location(
                                    building.world_coords, None
                                )
                                return True
                return False
        if order.order_move_to_location:
            distance = engine.math_2d.get_distance(
                self.owner.world_coords, order.world_coords
            )
            if distance > close_distance:
                # in a vehicle
                if self.owner.ai.in_vehicle():
                    vehicle_order = VehicleOrder()
                    vehicle_order.order_drive_to_coords = True
                    vehicle_order.world_coords = copy.copy(order.world_coords)
                    if self.owner.ai.memory["task_vehicle_crew"][
                        "vehicle_role"
                    ].vehicle.ai.is_transport:
                        vehicle_order.exit_vehicle_when_finished = True

                    # the driver will grab this when out of orders
                    self.owner.ai.memory["task_vehicle_crew"]["vehicle_order"] = vehicle_order
                    return True
                # we must be on foot
                self.owner.ai.switch_task_move_to_location(order.world_coords, None)
                return True
            else:
                # close enough. order is complete
                orders.remove(order)
                return False

        # default
        return False

    # ---------------------------------------------------------------------------
    def tactical_decision(self):
        """the squad leader makes a tactical decision and generates a new order"""

        # close_world_area=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.world_areas,3000)

        # - are we currently in combat?

        if len(self.owner.ai.human_targets + self.owner.ai.vehicle_targets) > 0:
            if len(self.owner.ai.vehicle_targets) > len(self.owner.ai.squad.vehicles):
                # lets get out of here
                friendly_area = None
                for area in self.owner.world.world_areas:
                    if area.faction == self.owner.ai.squad.faction:
                        friendly_area = area
                        break
                if friendly_area is not None:
                    tactical_order = TacticalOrder()
                    tactical_order.order_move_to_location = True
                    tactical_order.world_coords = copy.copy(
                        friendly_area.get_location()
                    )
                    self.owner.ai.memory["task_squad_leader"]["orders"].append(tactical_order)

                    self.owner.ai.add_journal_entry(f"Ordered squad to fall back to {friendly_area.name}")
                    self.owner.ai.speak(f"Squad fall back to {friendly_area.name}!")

                    return

            # default - stay and fight. do we need a order here ?
            return

        # - defend a contested area -
        contested_area = None
        for area in self.owner.world.world_areas:
            if area.is_contested:
                contested_area = area
                break
        if contested_area is not None:
            tactical_order = TacticalOrder()
            tactical_order.order_defend_area = True
            tactical_order.world_coords = copy.copy(contested_area.get_location())
            tactical_order.world_area = contested_area
            self.owner.ai.memory["task_squad_leader"]["orders"].append(tactical_order)
            self.owner.ai.add_journal_entry(f"Ordered squad to defend {contested_area.name}")
            return

        # - move to a random area -
        random_area = random.choice(self.owner.world.world_areas)
        tactical_order = TacticalOrder()
        tactical_order.order_move_to_location = True
        tactical_order.world_coords = copy.copy(random_area.get_location())
        self.owner.ai.memory["task_squad_leader"]["orders"].append(tactical_order)
        self.owner.ai.add_journal_entry(f"Ordered squad to move to {random_area.name}")
        return

    # ---------------------------------------------------------------------------
    def think_fast(self):
        # -- do the shorter thing --

        if self.owner.ai.in_building:
            self.owner.ai.squad.max_distance_human = 75
        else:
            self.owner.ai.squad.max_distance_human = 300

        # building cover: head to closest building on recent fire (or while defending)
        building = self.owner.ai.closest_building
        if building is not None:
            orders = self.owner.ai.memory["task_squad_leader"]["orders"]
            has_defend_order = any(o.order_defend_area for o in orders)

            recent_fire = (
                self.owner.grid_square.last_gun_fired + 30 > self.owner.world.world_seconds
            )

            bdist = engine.math_2d.get_distance(
                self.owner.world_coords, building.world_coords
            )
            cover_dist = building.collision_radius * 0.5
            if bdist > cover_dist and (has_defend_order or recent_fire):
                if not self.owner.ai.in_vehicle():
                    self.owner.ai.switch_task_move_to_location(
                        building.world_coords, None
                    )
                    self.owner.ai.speak(f"Take cover in that {building.name}")


    # ---------------------------------------------------------------------------
    def think_slow(self):
        # reset time
        self.owner.ai.memory["task_squad_leader"]["last_think_time"] = (
            self.owner.world.world_seconds
        )

        # re-randomize for next think (0.5s to 5s)
        self.owner.ai.memory["task_squad_leader"]["think_interval"] = random.uniform(
            0.5, 5.0
        )

        # -- do the longer thing ---
        self.review_orders()

    # ---------------------------------------------------------------------------
    def update_task_squad_leader(self):
        """Squad leader AI task for temporary tactical oversight"""

        last_think_time = self.owner.ai.memory["task_squad_leader"]["last_think_time"]
        think_interval = self.owner.ai.memory["task_squad_leader"]["think_interval"]

        if self.owner.world.world_seconds - last_think_time > think_interval:
            self.think_slow()
        else:
            self.think_fast()

        # if we reached the end still in task_squad_leader, yield to general think
        # so the leader periodically runs full priorities (threats, ammo, medic, etc.)
        if self.owner.ai.memory.get("current_task") == "task_squad_leader":
            self.owner.ai.switch_task_think()
