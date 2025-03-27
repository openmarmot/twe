'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : 

dynamically builds squads when the world is loaded

# ref

'''

#import built in modules
import copy

#import custom modules
import engine.world_builder
from ai.ai_squad import AISquad

#------------------------------------------------------------------------------
def create_squads(world_objects):
    ''' new style create squads'''
    # -- 1. build the squad objects dict --
    squad_objects={}
    for b in world_objects:
        if b.is_human or b.is_vehicle:
            if b.world_builder_identity in squad_objects:
                squad_objects[b.world_builder_identity].append(b)
            else:
                squad_objects[b.world_builder_identity]=[b]

    # -- 2. create the standard squads based on engine.world_builder.squad_data --
    squads = []
    while True:
        squad_made = False
        for squad_definition in engine.world_builder.squad_data.values():
            # Check if squad can be formed
            required = {}
            for identity in squad_definition['members'].split(','):

                required[identity] = required.get(identity, 0) + 1
            can_form = all(len(squad_objects.get(identity, [])) >= count for identity, count in required.items())

            if can_form:
                # Form the squad
                current_squad = []
                for identity in squad_definition['members'].split(','):
                    current_squad.append(squad_objects[identity].pop(0))
                squads.append(current_squad)
                squad_made = True
                break  # Move to next iteration
        if not squad_made:
            break  # No more squads possible

    # -- 3. create the erstatz squads --
    remaining_objects = [obj for identity in squad_objects for obj in squad_objects[identity]]    
    additional_squads = [remaining_objects[i:i+7] for i in range(0, len(remaining_objects), 7)]
    squads.extend(additional_squads)
    return squads


