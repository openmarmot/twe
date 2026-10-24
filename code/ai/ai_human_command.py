"""
repo : https://github.com/openmarmot/twe

notes : command group leader. on a slow think he claims squads near him,
keeps a plan for the fight he is trying to win, and pulls those squads
back when that fight is lost. his own men still follow him.
"""

# import built in modules
import random
import copy

# import custom packages
import engine.math_2d
from engine.tactical_order import TacticalOrder
from engine.vehicle_order import VehicleOrder


# a squad this close to its order point has arrived
ARRIVED_DISTANCE = 300

# the command group starts walking once it is farther than this from its hold
HOLD_DISTANCE = 400

# a squad leader within this distance of the field commander can be commanded.
# the squad's position is the squad leader's position.
CONTROL_DISTANCE = 10000

# reach when a man in the command squad carries a radio, or the commander
# is in a vehicle that has one
RADIO_CONTROL_DISTANCE = 20000

# seconds before the same squad can be given another attack order
RETASK_SECONDS = 90

# watch a fight this long before it can be called lost
SETTLE_SECONDS = 60

# do not march back into an area given up until this long has passed
ABANDON_SECONDS = 180

# enemy count at or above this multiple of the friendly count is a loss
LOST_OUTNUMBER = 2


class AIHumanCommand:
    def __init__(self, owner):
        self.owner = owner

    # ---------------------------------------------------------------------------
    def abandon_area(self, area):
        """remember that this fight was given up, and drop it as the objective"""

        plan = self.plan()
        plan["abandoned"][area] = self.owner.world.world_seconds
        plan["watched"].pop(area, None)
        if plan["objective"] is area:
            plan["objective"] = None

    # ---------------------------------------------------------------------------
    def area_is_ours(self, area):
        """true when our faction holds the area and nobody is fighting for it"""

        faction = self.owner.ai.squad.faction
        if area.faction != faction:
            return False
        if area.is_contested:
            return False
        return True

    # ---------------------------------------------------------------------------
    def area_on_cooldown(self, area):
        """true when this area was given up too recently to attack again"""

        plan = self.plan()
        started = plan["abandoned"].get(area)
        if started is None:
            return False
        tactical = self.owner.ai.squad.faction_tactical
        enemy = tactical.get_area_enemy_count(area) or 0
        # the enemy left. it can be tried again
        if area.is_contested is False and enemy <= 0:
            plan["abandoned"].pop(area, None)
            return False
        elapsed = self.owner.world.world_seconds - started
        if elapsed >= ABANDON_SECONDS:
            plan["abandoned"].pop(area, None)
            return False
        return True

    # ---------------------------------------------------------------------------
    def choose_hold(self):
        """stand the command group on the same rear area squads fall back to"""

        fallback = self.plan().get("fallback")
        task_mem = self.owner.ai.memory["task_command"]
        if fallback is not None:
            task_mem["hold_coords"] = copy.copy(fallback.world_coords)
        else:
            spawn = self.owner.ai.squad.faction_tactical.spawn_location
            task_mem["hold_coords"] = copy.copy(spawn)

    # ---------------------------------------------------------------------------
    def claim_squad(self, squad, distance, control_distance):
        """take an unclaimed squad when this commander is the closest in range"""

        if distance is None or distance > control_distance:
            return False
        if self.closer_commander(squad.squad_leader.world_coords, distance):
            return False
        squad.command_squad = self.owner.ai.squad
        return True

    # ---------------------------------------------------------------------------
    def closer_commander(self, leader_coords, my_distance):
        """true when another living field commander is closer to this leader"""

        tactical = self.owner.ai.squad.faction_tactical
        for squad in tactical.squads:
            commander = squad.field_commander()
            if commander is None or commander is self.owner:
                continue
            if commander.ai.blood_pressure < 1:
                continue
            distance = engine.math_2d.get_distance(
                commander.world_coords, leader_coords
            )
            if distance > commander.ai.command_ai.command_range():
                continue
            if distance < my_distance:
                return True
            # a tie goes to one commander so both do not claim the squad
            if distance == my_distance and commander.name < self.owner.name:
                return True
        return False

    # ---------------------------------------------------------------------------
    def command_range(self):
        """how far this commander can hold a squad"""

        if self.has_command_radio():
            return RADIO_CONTROL_DISTANCE
        return CONTROL_DISTANCE

    # ---------------------------------------------------------------------------
    def cover_counts(self, squads):
        """how many subordinate squads already have an order for each area"""

        counts = {}
        for squad in squads:
            order = self.subordinate_order(squad)
            if order is None or order.world_area is None:
                continue
            area = order.world_area
            counts[area] = counts.get(area, 0) + 1
        return counts

    # ---------------------------------------------------------------------------
    def defenders_gone(self, area):
        """true when friendlies were in the area and the latest count is zero"""

        watch = self.plan()["watched"].get(area)
        if watch is None or len(watch["samples"]) < 2:
            return False
        previous = watch["samples"][-2][1]
        latest = watch["samples"][-1][1]
        if previous > 0 and latest <= 0:
            return True
        return False

    # ---------------------------------------------------------------------------
    def ensure_memory(self):
        """task_command memory, including the plan kept on this commander"""

        task_name = "task_command"
        if task_name not in self.owner.ai.memory:
            self.owner.ai.memory[task_name] = {
                "last_think_time": -100,
                "think_interval": 0,
                "hold_coords": None,
            }
        task_mem = self.owner.ai.memory[task_name]
        if "plan" not in task_mem:
            # objective: the area he is trying to take or hold
            # fallback: rear area beaten squads move to
            # watched: area -> {since, samples of (time, friendly, enemy)}
            # abandoned: area -> world_seconds it was given up
            # strength: squad id -> {area, count} when first ordered there
            task_mem["plan"] = {
                "objective": None,
                "fallback": None,
                "watched": {},
                "abandoned": {},
                "strength": {},
            }
        return task_mem

    # ---------------------------------------------------------------------------
    def fallback_area(self, objective):
        """the uncontested friendly area closest to the faction spawn"""

        tactical = self.owner.ai.squad.faction_tactical
        faction = tactical.faction
        spawn = tactical.spawn_location
        best = None
        best_distance = None
        for area in self.owner.world.world_areas:
            if area is objective:
                continue
            if area.faction != faction:
                continue
            if area.is_contested:
                continue
            distance = engine.math_2d.get_distance(spawn, area.world_coords)
            if best is None or distance < best_distance:
                best = area
                best_distance = distance
        return best

    # ---------------------------------------------------------------------------
    def fight_is_lost(self, area, controlled):
        """true when squads ordered here are in a fight that is going against us"""

        committed = self.squads_ordered_to(controlled, area)
        if len(committed) == 0:
            return False
        watch = self.plan()["watched"].get(area)
        if watch is None:
            return False
        elapsed = self.owner.world.world_seconds - watch["since"]
        if elapsed < SETTLE_SECONDS:
            return False
        samples = watch["samples"]
        if len(samples) < 2:
            return False
        earlier_friendly = None
        if len(samples) >= 3:
            earlier_friendly = samples[-3][1]
        previous = samples[-2]
        latest = samples[-1]
        previous_bad = self.reading_is_bad(
            previous[1], previous[2], earlier_friendly
        )
        latest_bad = self.reading_is_bad(latest[1], latest[2], previous[1])
        if previous_bad and latest_bad:
            return True
        # a squad cut in half, with the enemy already ahead, is lost too
        if latest[2] > latest[1]:
            for squad in committed:
                record = self.plan()["strength"].get(id(squad))
                if record is None or record["area"] is not area:
                    continue
                if record["count"] <= 0:
                    continue
                if len(squad.members) * 2 <= record["count"]:
                    return True
        return False

    # ---------------------------------------------------------------------------
    def has_command_radio(self):
        """true when the command squad can give orders by radio"""

        for member in self.owner.ai.squad.members:
            pickup = member.ai.large_pickup
            if pickup is not None and pickup.is_radio:
                return True
            if member.ai.in_vehicle() is False:
                continue
            crew = member.ai.memory.get("task_vehicle_crew")
            if crew is None:
                continue
            role = crew.get("vehicle_role")
            if role is None:
                continue
            # a command-squad man in the radio operator seat
            if role.is_radio_operator:
                return True
            # the commander riding in a vehicle that has a radio
            if member is self.owner and role.vehicle is not None:
                if role.vehicle.ai.radio is not None:
                    return True
        return False

    # ---------------------------------------------------------------------------
    def issue_objectives(self):
        """give one idle squad a defend order. the plan's objective comes first"""

        controlled = self.owner.ai.squad.commanded_squads
        if len(controlled) == 0:
            return
        priority = self.priority_areas()
        if len(priority) == 0:
            return

        plan = self.plan()
        counts = self.cover_counts(controlled)
        target = None
        objective = plan["objective"]
        if objective is not None and objective in priority:
            if counts.get(objective, 0) == 0:
                if self.area_on_cooldown(objective) is False:
                    target = objective

        if target is None:
            target = self.pick_uncovered(priority, counts, objective)
        if target is None:
            return

        eligible = []
        for squad in controlled:
            if self.subordinate_eligible(squad, priority) is False:
                continue
            order = self.subordinate_order(squad)
            if order is not None and order.world_area is target:
                continue
            eligible.append(squad)
        if len(eligible) == 0:
            return

        # with several squads, the one closest to the commander stays back
        if len(controlled) >= 3 and len(eligible) > 1:
            reserve = self.nearest_squad(eligible, self.owner.world_coords)
            eligible.remove(reserve)
            if len(eligible) == 0:
                return

        chosen = self.nearest_squad(eligible, target.world_coords)
        self.write_defend(chosen, target)

    # ---------------------------------------------------------------------------
    def keep_hold_position(self):
        """walk the command group to its hold when it has drifted off"""

        if self.owner.ai.in_vehicle():
            return
        hold = self.owner.ai.memory["task_command"].get("hold_coords")
        if hold is None:
            return
        distance = engine.math_2d.get_distance(self.owner.world_coords, hold)
        if distance > HOLD_DISTANCE:
            self.owner.ai.switch_task_move_to_location(hold, None)

    # ---------------------------------------------------------------------------
    def leader_distance(self, squad):
        """distance from this commander to the squad leader, or None"""

        leader = squad.squad_leader
        if leader is None:
            return None
        if leader.ai.blood_pressure < 1:
            return None
        return engine.math_2d.get_distance(
            self.owner.world_coords, leader.world_coords
        )

    # ---------------------------------------------------------------------------
    def maybe_think(self):
        """slow think. claim nearby squads, then follow or abandon the plan"""

        if self.owner.ai.is_field_commander is False:
            return

        task_mem = self.ensure_memory()
        elapsed = self.owner.world.world_seconds - task_mem["last_think_time"]
        if task_mem["think_interval"] > 0 and elapsed < task_mem["think_interval"]:
            return

        task_mem["last_think_time"] = self.owner.world.world_seconds
        task_mem["think_interval"] = random.uniform(20, 45)

        controlled = self.refresh_controlled_squads()
        self.sample_plan(controlled)
        self.recall_lost_fights(controlled)
        self.revise_plan()
        self.issue_objectives()
        self.choose_hold()

    # ---------------------------------------------------------------------------
    def nearest_squad(self, squads, coords):
        """the squad whose leader is closest to coords"""

        chosen = squads[0]
        chosen_distance = engine.math_2d.get_distance(
            chosen.squad_leader.world_coords, coords
        )
        for squad in squads[1:]:
            distance = engine.math_2d.get_distance(
                squad.squad_leader.world_coords, coords
            )
            if distance < chosen_distance:
                chosen = squad
                chosen_distance = distance
        return chosen

    # ---------------------------------------------------------------------------
    def pick_objective(self):
        """the contested or hostile area this commander will try to win"""

        tactical = self.owner.ai.squad.faction_tactical
        choices = []
        for area in self.priority_areas():
            if self.area_on_cooldown(area):
                continue
            choices.append(area)
        if len(choices) == 0:
            return None
        choices.sort(
            key=lambda area: (
                0 if area.is_contested else 1,
                -(tactical.get_area_enemy_count(area) or 0),
            )
        )
        return choices[0]

    # ---------------------------------------------------------------------------
    def pick_uncovered(self, priority, counts, objective):
        """an uncovered priority area, preferring the plan objective"""

        tactical = self.owner.ai.squad.faction_tactical
        uncovered = []
        for area in priority:
            if counts.get(area, 0) > 0:
                continue
            if self.area_on_cooldown(area):
                continue
            uncovered.append(area)
        if len(uncovered) == 0:
            return None
        uncovered.sort(
            key=lambda area: (
                0 if area is objective else 1,
                0 if area.is_contested else 1,
                -(tactical.get_area_enemy_count(area) or 0),
            )
        )
        return uncovered[0]

    # ---------------------------------------------------------------------------
    def plan(self):
        """the plan dict stored on this commander's task memory"""

        return self.ensure_memory()["plan"]

    # ---------------------------------------------------------------------------
    def priority_areas(self):
        """contested areas, then areas held by a hostile faction"""

        tactical = self.owner.ai.squad.faction_tactical
        areas = []
        for area in self.owner.world.world_areas:
            if area.is_contested:
                areas.append(area)
            elif area.faction in tactical.hostile_factions:
                areas.append(area)
        return areas

    # ---------------------------------------------------------------------------
    def pull_back(self, controlled, area):
        """order squads on this area to move to the rear rally point"""

        fallback = self.plan().get("fallback")
        if fallback is None or fallback is area:
            tactical = self.owner.ai.squad.faction_tactical
            dest_name = "the rear"
            dest_coords = copy.copy(tactical.spawn_location)
            use_area_locations = False
        else:
            dest_name = fallback.name
            dest_coords = None
            use_area_locations = True

        ordered = False
        for squad in self.squads_ordered_to(controlled, area):
            leader = squad.squad_leader
            if leader is None:
                continue
            if use_area_locations:
                dest_coords = copy.copy(fallback.get_location())
            order = TacticalOrder()
            order.order_move_to_location = True
            order.world_coords = copy.copy(dest_coords)
            leader.ai.give_squad_order(order)
            self.release_leader(leader, order.world_coords)
            squad.last_command_order_time = self.owner.world.world_seconds
            self.owner.ai.add_journal_entry(
                f"Ordered {leader.name} to fall back from {area.name} to {dest_name}"
            )
            leader.ai.add_journal_entry(
                f"Order from {self.owner.name}: fall back to {dest_name}"
            )
            self.owner.ai.speak(f"{leader.name}, fall back to {dest_name}")
            ordered = True

        if ordered is False:
            self.owner.ai.add_journal_entry(f"Gave up {area.name}")
        self.abandon_area(area)

    # ---------------------------------------------------------------------------
    def reading_is_bad(self, friendly, enemy, earlier_friendly):
        """true when this one count says the fight is going against us"""

        if friendly <= 0:
            return False
        if enemy >= friendly * LOST_OUTNUMBER:
            return True
        if earlier_friendly is None:
            return False
        if enemy > friendly and friendly < earlier_friendly:
            return True
        return False

    # ---------------------------------------------------------------------------
    def recall_lost_fights(self, controlled):
        """pull squads off every area this commander has lost"""

        # fallback is chosen before the recall so the move has somewhere to go
        objective = self.plan().get("objective")
        self.plan()["fallback"] = self.fallback_area(objective)

        areas = []
        for squad in controlled:
            order = self.subordinate_order(squad)
            if order is None or order.world_area is None:
                continue
            area = order.world_area
            if area in areas:
                continue
            if self.fight_is_lost(area, controlled) or self.defenders_gone(area):
                areas.append(area)
        for area in areas:
            self.pull_back(controlled, area)

    # ---------------------------------------------------------------------------
    def refresh_controlled_squads(self):
        """claim squads near this commander and release the ones who have left.

        a squad whose command_squad is another living commander is left alone.
        a squad this commander holds is released once its leader is beyond
        his command range. a radio stretches that range. a command group
        whose field commander is dead is cleared so someone else can claim it.
        """

        my_squad = self.owner.ai.squad
        tactical = my_squad.faction_tactical
        control_distance = self.command_range()
        controlled = []
        for squad in tactical.squads:
            if squad is my_squad:
                continue
            if len(squad.members) == 0:
                if squad.command_squad is my_squad:
                    squad.command_squad = None
                continue
            if squad.field_commander() is not None:
                continue
            if self.squad_has_player(squad):
                if squad.command_squad is my_squad:
                    squad.command_squad = None
                continue

            # a dead commander's claim should not keep the squad out of the war
            other = squad.command_squad
            if other is not None and other is not my_squad:
                if other.field_commander() is None:
                    squad.command_squad = None
                else:
                    continue

            distance = self.leader_distance(squad)
            if squad.command_squad is my_squad:
                # no leader yet: keep the claim until someone is elected
                if distance is None:
                    controlled.append(squad)
                    continue
                if distance > control_distance:
                    squad.command_squad = None
                    continue
                controlled.append(squad)
                continue

            if self.claim_squad(squad, distance, control_distance):
                controlled.append(squad)

        my_squad.commanded_squads = controlled
        return controlled

    # ---------------------------------------------------------------------------
    def release_leader(self, leader, dest_coords):
        """drop the current fight so a fall-back order is acted on"""

        if leader.ai.in_vehicle():
            crew = leader.ai.memory.get("task_vehicle_crew")
            if crew is None:
                return
            # is_retreat is kept by the driver ahead of a close-with order
            vehicle_order = VehicleOrder()
            vehicle_order.order_drive_to_coords = True
            vehicle_order.world_coords = copy.copy(dest_coords)
            vehicle_order.is_retreat = True
            crew["vehicle_order"] = vehicle_order
            return
        if leader.ai.memory.get("current_task") == "task_engage_enemy":
            leader.ai.memory.pop("task_engage_enemy", None)
            leader.ai.memory["current_task"] = "task_squad_leader"

    # ---------------------------------------------------------------------------
    def revise_plan(self):
        """keep one objective, and a rear area to fall back to"""

        plan = self.plan()
        objective = plan["objective"]
        if objective is not None:
            still_there = objective in self.owner.world.world_areas
            if still_there is False or self.area_is_ours(objective):
                plan["watched"].pop(objective, None)
                plan["objective"] = None
            elif self.area_on_cooldown(objective):
                plan["objective"] = None
        if plan["objective"] is None:
            plan["objective"] = self.pick_objective()
        plan["fallback"] = self.fallback_area(plan["objective"])

    # ---------------------------------------------------------------------------
    def sample_plan(self, controlled):
        """record friendly and enemy counts for areas our squads are ordered to"""

        plan = self.plan()
        tactical = self.owner.ai.squad.faction_tactical
        now = self.owner.world.world_seconds
        areas = []
        if plan["objective"] is not None:
            areas.append(plan["objective"])
        for squad in controlled:
            order = self.subordinate_order(squad)
            if order is None or order.world_area is None:
                continue
            if order.world_area not in areas:
                areas.append(order.world_area)
            record = plan["strength"].get(id(squad))
            if record is None or record["area"] is not order.world_area:
                plan["strength"][id(squad)] = {
                    "area": order.world_area,
                    "count": len(squad.members),
                }

        seen = []
        for area in areas:
            seen.append(area)
            friendly = tactical.get_area_friendly_count(area) or 0
            enemy = tactical.get_area_enemy_count(area) or 0
            watch = plan["watched"].get(area)
            if watch is None:
                watch = {"since": now, "samples": []}
                plan["watched"][area] = watch
            watch["samples"].append((now, friendly, enemy))
            if len(watch["samples"]) > 4:
                del watch["samples"][0]

        for area in list(plan["watched"].keys()):
            if area not in seen:
                plan["watched"].pop(area, None)

        living = []
        for squad in controlled:
            living.append(id(squad))
        for key in list(plan["strength"].keys()):
            if key not in living:
                plan["strength"].pop(key, None)

    # ---------------------------------------------------------------------------
    def squad_has_player(self, squad):
        """true when the player is in this squad"""

        for member in squad.members:
            if member.is_player:
                return True
        return False

    # ---------------------------------------------------------------------------
    def squads_ordered_to(self, squads, area):
        """controlled squads whose current order points at this area"""

        found = []
        for squad in squads:
            order = self.subordinate_order(squad)
            if order is None or order.world_area is None:
                continue
            if order.world_area is area:
                found.append(squad)
        return found

    # ---------------------------------------------------------------------------
    def subordinate_eligible(self, squad, priority):
        """true when this squad can take a new attack order"""

        leader = squad.squad_leader
        if leader is None:
            return False
        for member in squad.members:
            if member.is_player:
                return False
        if leader.ai.blood_pressure < 1:
            return False
        if leader.ai.human_targets or leader.ai.vehicle_targets:
            return False
        if leader.ai.memory.get("current_task") == "task_engage_enemy":
            return False
        if squad.last_command_order_time > 0:
            since = self.owner.world.world_seconds - squad.last_command_order_time
            if since < RETASK_SECONDS:
                return False

        order = self.subordinate_order(squad)
        if order is None:
            return True
        if order.world_coords is not None:
            distance = engine.math_2d.get_distance(
                leader.world_coords, order.world_coords
            )
            if distance > ARRIVED_DISTANCE:
                return False
        if order.world_area is not None and order.world_area in priority:
            return False
        return True

    # ---------------------------------------------------------------------------
    def subordinate_order(self, squad):
        """the squad leader's current tactical order, or None"""

        leader = squad.squad_leader
        if leader is None:
            return None
        task_mem = leader.ai.memory.get("task_squad_leader")
        if task_mem is None:
            return None
        orders = task_mem.get("orders")
        if orders is None or len(orders) == 0:
            return None
        return orders[0]

    # ---------------------------------------------------------------------------
    def update_task_command(self):
        """command group task. assigns objectives, then yields to general think"""

        if self.owner.ai.is_civilian or self.owner.ai.is_field_commander is False:
            self.owner.ai.switch_task_think()
            return

        self.maybe_think()
        self.keep_hold_position()

        # still on this task: go fight, scavenge, and heal like any other soldier
        if self.owner.ai.memory.get("current_task") == "task_command":
            self.owner.ai.switch_task_think()

    # ---------------------------------------------------------------------------
    def write_defend(self, squad, area):
        """defend order for one squad, aimed at a free point in the area"""

        tactical = self.owner.ai.squad.faction_tactical
        destination = copy.copy(area.get_location())
        order = TacticalOrder()
        order.order_defend_area = True
        order.world_area = area
        order.world_coords = destination
        order.threat_direction = tactical.get_threat_direction(destination)

        leader = squad.squad_leader
        leader.ai.give_squad_order(order)
        squad.last_command_order_time = self.owner.world.world_seconds
        self.owner.ai.add_journal_entry(
            f"Ordered {leader.name} to defend {area.name}"
        )
        leader.ai.add_journal_entry(
            f"Order from {self.owner.name}: defend {area.name}"
        )
        self.owner.ai.speak(f"{leader.name}, defend {area.name}")
