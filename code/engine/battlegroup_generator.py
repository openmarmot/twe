"""
repo : https://github.com/openmarmot/twe

notes :

battlegroup is a list of squads
camo variants share the base squad's chance roll, then one is picked at random
categories spend a share of funds. cheap infantry is counted at a minimum
slot cost so leftover points cannot buy hundreds of rifle squads.

# ref

"""

# import built in modules
import random

# squad types that should not clone when rare
vehicle_squad_types = [
    "tank",
    "antitank_vehicle",
    "fire_support_vehicle",
    "afv",
    "recon",
    "utility",
    "air",
    "towed_antitank",
    "towed_antiair",
]

gun_squad_types = [
    "towed_antitank",
    "towed_antiair",
    "artillery",
]

# cheap infantry-like types are billed at least this much against
# their category budget so they cannot convert leftover points into
# more squads than the sim can handle
cheap_slot_types = [
    "infantry",
    "motorized_infantry",
    "mechanized_infantry",
    "medic",
    "mechanic",
    "sniper",
    "infantry radio",
    "mg",
    "antitank_infantry",
]

# share of battlegroup funds each category may spend
category_share = {
    "infantry": 0.40,
    "tanks": 0.26,
    "antitank": 0.12,
    "support_infantry": 0.05,
    "support_vehicle": 0.08,
    "artillery": 0.07,
    "other": 0.02,
}

# ------------------------------------------------------------------------------


def get_camo_base_name(squad_name):
    """Return base squad name if this is a camo variant, else None"""

    marker = " camo"
    idx = squad_name.lower().find(marker)
    if idx == -1:
        return None
    after = squad_name[idx + len(marker) :]
    if after == "" or after.isdigit():
        return squad_name[:idx]
    return None


def get_camo_groups(squad_data):
    """Map base squad name to a list of camo variant names"""

    groups = {}
    for name in squad_data:
        base = get_camo_base_name(name)
        if base and base in squad_data:
            if base in groups:
                groups[base].append(name)
            else:
                groups[base] = [name]
    return groups


def pick_camo_variant(squad_name, camo_groups):
    """Randomly pick the base squad or one of its camo variants"""

    variants = [squad_name]
    if squad_name in camo_groups:
        variants += camo_groups[squad_name]
    return random.choice(variants)


def related_squad_names(squad_name, camo_groups):
    """Base squad plus its camo skins"""

    base = get_camo_base_name(squad_name)
    if base is None:
        base = squad_name
    names = [base]
    if base in camo_groups:
        names += camo_groups[base]
    return names


def count_related_squads(battlegroup, squad_name, camo_groups):
    """How many of this squad (including camo skins) are already in the force"""

    names = related_squad_names(squad_name, camo_groups)
    count = 0
    for s in battlegroup:
        if s in names:
            count += 1
    return count


def min_slot_cost(funds):
    """Accounting floor for cheap squads. Smaller fights use a smaller slot."""

    if funds < 1500:
        return 50
    return 100


def accounting_cost(unit_cost, unit_type, funds):
    """Points billed against a category budget for this squad"""

    if unit_type in cheap_slot_types:
        slot = min_slot_cost(funds)
        if unit_cost < slot:
            return slot
    return unit_cost


def name_share_for_type(unit_type):
    """Max fraction of a category one squad name may consume"""

    if unit_type in gun_squad_types:
        return 0.5
    if unit_type == "tank":
        return 0.75
    return 0.5


# ------------------------------------------------------------------------------


def create_random_battlegroup(faction, funds, squad_data, year=1944):
    """Create random battlegroup for a faction"""

    # we should break this out into its own file

    battlegroup = []
    cost = 0

    year_chance_key = f"chance_{year}"

    camo_groups = get_camo_groups(squad_data)

    # Sort faction-specific data into categories
    squad_options_tanks = {}
    squad_options_antitank = {}
    squad_options_infantry = {}
    squad_options_support_infantry = {}
    squad_options_support_vehicle = {}
    squad_options_artillery = {}
    squad_options_other = {}

    for key, value in squad_data.items():
        if get_camo_base_name(key) in camo_groups:
            continue
        if value["faction"] == faction:
            squad_chance = value.get(year_chance_key, 0)
            if random.randint(1, 100) > squad_chance:
                continue

            if value["type"] == "tank":
                squad_options_tanks[key] = value
            elif value["type"] in [
                "infantry",
                "motorized_infantry",
                "mechanized_infantry",
            ]:
                squad_options_infantry[key] = value
            elif value["type"] in [
                "medic",
                "mechanic",
                "sniper",
                "infantry radio",
                "mg",
            ]:
                squad_options_support_infantry[key] = value
            elif value["type"] in [
                "fire_support_vehicle",
                "towed_antiair",
                "recon",
                "afv",
            ]:
                squad_options_support_vehicle[key] = value
            elif value["type"] in ["artillery"]:
                squad_options_artillery[key] = value
            elif value["type"] in [
                "antitank_vehicle",
                "antitank_infantry",
                "towed_antitank",
            ]:
                squad_options_antitank[key] = value
            else:
                squad_options_other[key] = value

    cat_budget = {}
    cat_spent = {}
    for cat_name, share in category_share.items():
        cat_budget[cat_name] = int(funds * share)
        cat_spent[cat_name] = 0
    name_spent = {}

    def can_add(cat_name, squad_name, squad_info):
        unit_cost = squad_info["cost"]
        unit_type = squad_info.get("type", "")
        unit_chance = squad_info.get(year_chance_key, 0)
        acct = accounting_cost(unit_cost, unit_type, funds)
        if cost + unit_cost > funds:
            return False
        if cat_spent[cat_name] + acct > cat_budget[cat_name]:
            return False
        if (
            unit_chance < 50
            and unit_type in vehicle_squad_types
            and count_related_squads(battlegroup, squad_name, camo_groups) >= 1
        ):
            return False
        base = squad_name
        camo_base = get_camo_base_name(squad_name)
        if camo_base:
            base = camo_base
        name_cap = int(cat_budget[cat_name] * name_share_for_type(unit_type))
        spent = name_spent.get(base, 0)
        if spent + acct > name_cap:
            return False
        return True

    # Define categories with their batch ranges (min, max)
    categories = [
        (squad_options_infantry, 3, 5, "infantry"),
        (squad_options_tanks, 1, 3, "tanks"),
        (squad_options_antitank, 0, 2, "antitank"),
        (squad_options_support_infantry, 0, 3, "support_infantry"),
        (squad_options_support_vehicle, 0, 3, "support_vehicle"),
        (squad_options_artillery, 0, 2, "artillery"),
        (squad_options_other, 0, 2, "other"),
    ]

    while cost < funds:
        added = False
        # random.shuffle(categories)  # Randomize order to avoid bias

        for cat_dict, min_num, max_num, cat_name in categories:
            if cat_dict:
                available = []
                for k in cat_dict:
                    if can_add(cat_name, k, cat_dict[k]):
                        available.append(k)
                if not available:
                    continue
                random_key = random.choice(available)
                unit_cost = cat_dict[random_key]["cost"]
                unit_chance = cat_dict[random_key].get(year_chance_key, 0)
                unit_type = cat_dict[random_key].get("type", "")
                # rare vehicles (year chance < 50) are bought one at a time
                if (
                    unit_chance < 50
                    and unit_type in vehicle_squad_types
                ):
                    batch_count = 1
                else:
                    batch_count = random.randint(min_num, max_num)
                for _ in range(batch_count):
                    if not can_add(cat_name, random_key, cat_dict[random_key]):
                        break
                    acct = accounting_cost(unit_cost, unit_type, funds)
                    cost += unit_cost
                    cat_spent[cat_name] += acct
                    base = random_key
                    name_spent[base] = name_spent.get(base, 0) + acct
                    battlegroup.append(
                        pick_camo_variant(random_key, camo_groups)
                    )
                    added = True

        if not added:
            break  # category budgets full, or nothing left that fits

    return battlegroup
