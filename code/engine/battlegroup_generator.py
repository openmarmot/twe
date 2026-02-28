'''
repo : https://github.com/openmarmot/twe

notes : 

battlegroup is a list of squads 

# ref

'''
#import built in modules
import random

#------------------------------------------------------------------------------

def create_random_battlegroup(faction, funds,squad_data):
    '''Create random battlegroup for a faction'''

    # we should break this out into its own file
    
    battlegroup = []
    cost = 0

    # Sort faction-specific data into categories
    squad_options_tanks = {}
    squad_options_antitank = {}
    squad_options_infantry = {}
    squad_options_support_infantry = {}
    squad_options_support_vehicle = {}
    squad_options_artillery = {}
    squad_options_other = {}
    
    for key, value in squad_data.items():
        if value['faction'] == faction:
            if value['type'] == 'tank':
                squad_options_tanks[key] = value
            elif value['type'] in ['infantry', 'motorized_infantry', 'mechanized_infantry']:
                squad_options_infantry[key] = value
            elif value['type'] in ['medic', 'mechanic', 'sniper', 'infantry radio', 'mg']:
                squad_options_support_infantry[key] = value
            elif value['type'] in ['fire_support_vehicle', 'towed_antiair', 'scout car','afv']:
                squad_options_support_vehicle[key] = value
            elif value['type'] in ['artillery']:
                squad_options_artillery[key] = value
            elif value['type'] in ['antitank_vehicle','antitank_infantry','towed_antitank']:
                squad_options_antitank[key] = value
            else:
                squad_options_other[key] = value
    
    # Define categories with their batch ranges (min, max)
    categories = [
        (squad_options_infantry, 3, 5),
        (squad_options_tanks, 1, 3),
        (squad_options_antitank,0,4),
        (squad_options_support_infantry, 0, 3),
        (squad_options_support_vehicle, 0, 3),
        (squad_options_artillery,0,4),
        (squad_options_other, 0, 2)
    ]
    
    while cost < funds:
        added = False
        #random.shuffle(categories)  # Randomize order to avoid bias
        
        for cat_dict, min_num, max_num in categories:
            if cat_dict:
                random_key = random.choice(list(cat_dict.keys()))
                unit_cost = cat_dict[random_key]['cost']
                for i in range(random.randint(min_num, max_num)):
                    if cost + unit_cost <= funds:
                        cost += unit_cost
                        battlegroup.append(random_key)
                        added = True
                    else:
                        break  # No need to try more in this batch
        
        if not added:
            break  # Prevent infinite loop if can't afford anything
    
    return battlegroup