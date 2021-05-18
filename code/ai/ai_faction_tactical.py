
'''
module : ai_faction_tactical.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : AI that controls all a factions squads on the tactical map 
'''


#import built in modules
import random 

#import custom packages
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 21 2021' #date of last update


#global variables

class AIFactionTactical(object):
    def __init__(self):

        # squads in the faction who are present on this map
        self.squads=[] 

        # current ai state
        self.ai_state='none'

        # current ai goal
        self.ai_goal='none'

        # general map goal (attack/defend/scout ?)

    def spawn_on_map(self):
        for b in self.squads:
            # random locations is temporary for now
            b.world_coords=[float(random.randint(-1500,1500)),float(random.randint(-1500,1500))]
            b.destination=[float(random.randint(-200,200)),float(random.randint(-200,200))]
            
            b.spawn_on_map()

    def update(self):

        # run the update for each squad
        for b in self.squads:
            b.update()

        # set squad destinations to move squads around 


