"""
repo : https://github.com/openmarmot/twe

notes : civilian trader skill for ai_human
"""

# import built in modules
import random

# import custom packages
import engine.math_2d


class AIHumanTrader:
    """civilian trader skill. find a building, wait, then offer trade"""

    def __init__(self, owner):
        self.owner = owner

        # how close a customer must be before the trader walks over
        self.customer_notice_distance = 500
        # conversation range
        self.talk_distance = 25
        # do not re-approach the same person immediately
        self.customer_cooldown = 45

    # ---------------------------------------------------------------------------
    def abort_trader(self):
        """stop trading and go back to think"""
        self.owner.ai.memory.pop("task_trader", None)
        self.owner.ai.switch_task_think()

    # ---------------------------------------------------------------------------
    def arrive_at_building(self, building):
        """True when the trader is inside or well inside the building footprint"""
        if building is None:
            return False
        if self.owner.ai.in_building and building in self.owner.ai.building_list:
            return True
        distance = engine.math_2d.get_distance(
            self.owner.world_coords, building.world_coords
        )
        return distance < max(building.collision_radius * 0.4, 20)

    # ---------------------------------------------------------------------------
    def find_customer(self, task):
        """nearest eligible human within notice range. prefers the player"""
        last_customer = task["last_customer"]
        last_time = task["last_customer_time"]
        now = self.owner.world.world_seconds

        player = self.owner.world.player
        if player is not None and player is not self.owner:
            if self.customer_is_eligible(player, last_customer, last_time, now):
                distance = engine.math_2d.get_distance(
                    self.owner.world_coords, player.world_coords
                )
                if distance < self.customer_notice_distance:
                    return player

        humans = self.owner.world.grid_manager.get_objects_from_grid_squares_near_world_coords(
            self.owner.world_coords, self.customer_notice_distance, True, False
        )

        best = None
        best_distance = self.customer_notice_distance
        for human in humans:
            if human is self.owner:
                continue
            if not self.customer_is_eligible(human, last_customer, last_time, now):
                continue
            distance = engine.math_2d.get_distance(
                self.owner.world_coords, human.world_coords
            )
            if distance < best_distance:
                best_distance = distance
                best = human
        return best

    # ---------------------------------------------------------------------------
    def customer_is_eligible(self, human, last_customer, last_time, now):
        """True if this human can be asked to trade"""
        if human is None:
            return False
        if human.ai.blood_pressure < 1:
            return False
        if human.ai.memory.get("current_task") == "task_trader":
            return False
        if human is last_customer and now - last_time < self.customer_cooldown:
            return False
        return True

    # ---------------------------------------------------------------------------
    def find_trade_building(self):
        """pick a building. random in this square, else a nearby square that has one"""
        current = self.owner.grid_square
        if current.wo_objects_building:
            return random.choice(current.wo_objects_building)

        nearby = self.owner.world.grid_manager.get_grid_squares_near_world_coords(
            self.owner.world_coords, current.grid_size * 3
        )
        squares_with_buildings = [s for s in nearby if s.wo_objects_building]
        if squares_with_buildings:
            squares_with_buildings.sort(
                key=lambda s: engine.math_2d.get_distance(
                    self.owner.world_coords, list(s.center)
                )
            )
            return random.choice(squares_with_buildings[0].wo_objects_building)

        # last resort - any building on the map
        for square in self.owner.world.grid_manager.index_map.values():
            if square.wo_objects_building:
                return random.choice(square.wo_objects_building)
        return None

    # ---------------------------------------------------------------------------
    def offer_trade(self, customer):
        """ask the customer to trade. opens the trade menu for the player"""
        self.owner.ai.speak("Want to trade?")
        self.owner.ai.add_journal_entry("Offered to trade")

        if customer.is_player:
            self.owner.world.world_menu.open_trade_menu(self.owner)

    # ---------------------------------------------------------------------------
    def switch_task_trader(self):
        """switch to task_trader"""
        task_name = "task_trader"

        if task_name not in self.owner.ai.memory:
            task_details = {
                "status": "finding_building",
                "building": None,
                "customer": None,
                "last_customer": None,
                "last_customer_time": 0,
                "last_think_time": 0,
                "think_interval": 1.0,
            }
            self.owner.ai.memory[task_name] = task_details

        self.owner.ai.memory["current_task"] = task_name
        self.owner.ai.add_journal_entry("Looking for a place to trade")

    # ---------------------------------------------------------------------------
    def update_task_trader(self):
        """update task_trader"""
        ai = self.owner.ai

        recent_fire = (
            self.owner.grid_square.last_gun_fired + 30 > self.owner.world.world_seconds
        )
        if recent_fire:
            ai.memory.pop("task_trader", None)
            ai.civilian_flee_gunfire()
            return

        if "task_trader" not in ai.memory:
            ai.switch_task_think()
            return

        task = ai.memory["task_trader"]
        status = task["status"]

        if status == "finding_building":
            building = self.find_trade_building()
            if building is None:
                self.abort_trader()
                return
            task["building"] = building
            task["status"] = "moving_to_building"
            self.face_destination(building.world_coords)
            return

        if status == "moving_to_building":
            building = task["building"]
            if building is None or building.in_world is False:
                task["status"] = "finding_building"
                task["building"] = None
                return
            if self.arrive_at_building(building):
                task["status"] = "waiting"
                task["last_think_time"] = 0
                return
            self.walk_towards(building.world_coords)
            return

        if status == "waiting":
            building = task["building"]
            if building is None or building.in_world is False:
                task["status"] = "finding_building"
                task["building"] = None
                return
            if not self.arrive_at_building(building):
                task["status"] = "moving_to_building"
                return

            now = self.owner.world.world_seconds
            if now - task["last_think_time"] > task["think_interval"]:
                task["last_think_time"] = now
                task["think_interval"] = random.uniform(0.8, 1.6)
                customer = self.find_customer(task)
                if customer is not None:
                    task["customer"] = customer
                    task["status"] = "approaching"
                    self.face_destination(customer.world_coords)
            return

        if status == "approaching":
            customer = task["customer"]
            if not self.customer_is_eligible(
                customer, None, 0, self.owner.world.world_seconds
            ):
                task["customer"] = None
                task["status"] = "waiting"
                return

            distance = engine.math_2d.get_distance(
                self.owner.world_coords, customer.world_coords
            )
            if distance < self.talk_distance:
                self.offer_trade(customer)
                task["last_customer"] = customer
                task["last_customer_time"] = self.owner.world.world_seconds
                task["customer"] = None
                task["status"] = "waiting"
                return

            now = self.owner.world.world_seconds
            if now - task["last_think_time"] > 0.5:
                task["last_think_time"] = now
                self.face_destination(customer.world_coords)
            self.walk_towards(customer.world_coords)

    # ---------------------------------------------------------------------------
    def face_destination(self, destination):
        """face the walk destination"""
        self.owner.rotation_angle = engine.math_2d.get_rotation(
            self.owner.world_coords, destination
        )
        self.owner.reset_image = True

    # ---------------------------------------------------------------------------
    def walk_towards(self, destination):
        """walk one frame toward destination"""
        ai = self.owner.ai
        self.owner.world_coords = engine.math_2d.moveTowardsTarget(
            ai.get_calculated_speed(),
            self.owner.world_coords,
            destination,
            self.owner.world.time_passed_seconds,
        )
        ai.recent_noise_or_move = True
        ai.last_noise_or_move_time = self.owner.world.world_seconds
        ai.fatigue += ai.fatigue_add_rate * self.owner.world.time_passed_seconds
