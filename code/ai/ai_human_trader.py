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
        # [human, last_contact_world_seconds, cooldown_seconds]
        self.contact_list = []
        # 2 to 5 minutes
        self.contact_cooldown_min = 120
        self.contact_cooldown_max = 300
        # low chance per waiting-think to react to other traders in this square
        self.crowding_react_chance = 0.025

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
    def find_customer(self):
        """nearest eligible human within notice range. prefers the player"""
        now = self.owner.world.world_seconds

        player = self.owner.world.player
        if player is not None and player is not self.owner:
            if self.customer_is_eligible(player, now):
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
            if not self.customer_is_eligible(human, now):
                continue
            distance = engine.math_2d.get_distance(
                self.owner.world_coords, human.world_coords
            )
            if distance < best_distance:
                best_distance = distance
                best = human
        return best

    # ---------------------------------------------------------------------------
    def contact_cooled_down(self, human, now):
        """True if this trader's last contact with human is old enough"""
        for entry in self.contact_list:
            if entry[0] is human:
                return now - entry[1] >= entry[2]
        return True

    # ---------------------------------------------------------------------------
    def customer_is_eligible(self, human, now, ignore_cooldown=False):
        """True if this human can be asked to trade"""
        if human is None:
            return False
        if human.ai.blood_pressure < 1:
            return False
        if "task_trader" in human.ai.memory:
            return False
        if ignore_cooldown:
            return True
        if not self.contact_cooled_down(human, now):
            return False
        last = human.ai.last_trader_contact_time
        cooldown = human.ai.last_trader_contact_cooldown
        if last > 0 and now - last < cooldown:
            return False
        if self.human_claimed_by_other_trader(human):
            return False
        return True

    # ---------------------------------------------------------------------------
    def find_trade_building(self, exclude_square=None):
        """pick a building. random in this square, else a nearby square that has one"""
        current = self.owner.grid_square

        if exclude_square is None and current.wo_objects_building:
            return random.choice(current.wo_objects_building)

        nearby = self.owner.world.grid_manager.get_grid_squares_near_world_coords(
            self.owner.world_coords, current.grid_size * 3
        )
        squares_with_buildings = [
            s
            for s in nearby
            if s.wo_objects_building and s is not exclude_square
        ]
        if squares_with_buildings:
            squares_with_buildings.sort(
                key=lambda s: engine.math_2d.get_distance(
                    self.owner.world_coords, list(s.center)
                )
            )
            return random.choice(squares_with_buildings[0].wo_objects_building)

        # last resort - any building on the map
        for square in self.owner.world.grid_manager.index_map.values():
            if square is exclude_square:
                continue
            if square.wo_objects_building:
                return random.choice(square.wo_objects_building)
        return None

    # ---------------------------------------------------------------------------
    def human_claimed_by_other_trader(self, human):
        """True if another trader is already walking up to this human"""
        nearby = self.owner.world.grid_manager.get_objects_from_grid_squares_near_world_coords(
            self.owner.world_coords, self.customer_notice_distance, True, False
        )
        for other in nearby:
            if other is self.owner:
                continue
            other_task = other.ai.memory.get("task_trader")
            if other_task is None:
                continue
            if other_task.get("customer") is human:
                return True
        return False

    # ---------------------------------------------------------------------------
    def other_traders_in_square(self):
        """other humans in this grid square who are currently traders"""
        others = []
        for human in self.owner.grid_square.wo_objects_human:
            if human is self.owner:
                continue
            if human.ai.blood_pressure < 1:
                continue
            if "task_trader" in human.ai.memory:
                others.append(human)
        return others

    # ---------------------------------------------------------------------------
    def record_contact(self, human):
        """remember this approach and stamp the human so other traders wait"""
        now = self.owner.world.world_seconds
        cooldown = random.uniform(self.contact_cooldown_min, self.contact_cooldown_max)
        found = False
        for entry in self.contact_list:
            if entry[0] is human:
                entry[1] = now
                entry[2] = cooldown
                found = True
                break
        if found is False:
            self.contact_list.append([human, now, cooldown])
        human.ai.last_trader_contact_time = now
        human.ai.last_trader_contact_cooldown = cooldown

    # ---------------------------------------------------------------------------
    def maybe_react_to_other_traders(self, task):
        """low chance to stop or relocate if this square already has traders"""
        if not self.other_traders_in_square():
            return False
        if random.random() > self.crowding_react_chance:
            return False

        if random.randint(0, 1) == 0:
            self.owner.ai.add_journal_entry("Too many traders here, stopping")
            self.abort_trader()
            return True

        building = self.find_trade_building(exclude_square=self.owner.grid_square)
        if building is None:
            self.owner.ai.add_journal_entry("Too many traders here, stopping")
            self.abort_trader()
            return True

        self.owner.ai.add_journal_entry("Too many traders here, moving on")
        task["building"] = building
        task["customer"] = None
        task["status"] = "moving_to_building"
        self.owner.ai.switch_task_move_to_location(building.world_coords, None)
        return True

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
                "last_think_time": 0,
                "think_interval": 1.0,
            }
            self.owner.ai.memory[task_name] = task_details

        self.owner.ai.memory["current_task"] = task_name
        self.owner.ai.add_journal_entry("Looking for a place to trade")

    # ---------------------------------------------------------------------------
    def update_task_trader(self):
        """update task_trader.

        walking uses task_move_to_location. task_trader stays in memory so
        update_task_think resumes it when the walk finishes.
        """
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

        if task["status"] == "finding_building":
            building = self.find_trade_building()
            if building is None:
                self.abort_trader()
                return
            task["building"] = building
            task["status"] = "moving_to_building"

        if task["status"] == "moving_to_building":
            building = task["building"]
            if building is None or building.in_world is False:
                task["status"] = "finding_building"
                task["building"] = None
                return
            if self.arrive_at_building(building):
                task["status"] = "waiting"
                task["last_think_time"] = 0
            else:
                ai.switch_task_move_to_location(building.world_coords, None)
                return

        if task["status"] == "waiting":
            building = task["building"]
            if building is None or building.in_world is False:
                task["status"] = "finding_building"
                task["building"] = None
                return
            if not self.arrive_at_building(building):
                task["status"] = "moving_to_building"
                ai.switch_task_move_to_location(building.world_coords, None)
                return

            now = self.owner.world.world_seconds
            if now - task["last_think_time"] > task["think_interval"]:
                task["last_think_time"] = now
                task["think_interval"] = random.uniform(0.8, 1.6)
                if self.maybe_react_to_other_traders(task):
                    return
                customer = self.find_customer()
                if customer is not None:
                    task["customer"] = customer
                    task["status"] = "approaching"
                    self.record_contact(customer)

        if task["status"] == "approaching":
            customer = task["customer"]
            if not self.customer_is_eligible(
                customer, self.owner.world.world_seconds, ignore_cooldown=True
            ):
                task["customer"] = None
                task["status"] = "waiting"
                return

            distance = engine.math_2d.get_distance(
                self.owner.world_coords, customer.world_coords
            )
            if distance < self.talk_distance:
                self.offer_trade(customer)
                self.record_contact(customer)
                task["customer"] = None
                task["status"] = "waiting"
                return

            # moving_object so the walk tracks the customer if they move
            ai.switch_task_move_to_location(customer.world_coords, customer)
