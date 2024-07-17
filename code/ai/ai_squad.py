
'''
module : ai_group.py
language : Python 3.x
email : andrew@openmarmot.com
notes : holds some squad specific variables
most of the logic should be in ai_human
'''


#import built in modules
import random 
import copy

#import custom packages
import engine.math_2d

#global variables

class AISquad(object):
    def __init__(self,world):

        self.world=world

        # destination - this is set by the faction tactical ai
        self.destination=[0.,0.]
        
        # people in the squad 
        # ai_human will remove itself on death 
        self.members=[]

        # world_object squad member who is the leader.
        # squad memebers will self elect and update this 
        # however if the squad is busy it might take a minute
        self.squad_leader=None

        # vehicles that the squad spawned with. 
        self.starting_vehicles=[]


        # faction - german/soviet/american/civilian
        self.faction='none'

        # a link back to the parent faction tactical
        # set in ai_faction_tactical.process_spawn_queue()
        self.faction_tactical=None

    #---------------------------------------------------------------------------
    def add_to_squad(self, WORLD_OBJECT):
        ''' add a world_object to the squad. DOES NOT SPAWN AT THE MOMENT'''
        if WORLD_OBJECT.is_human==False:
            print('error: attempting to add a non human to squad')
        

        # remmove from the old squad
        if WORLD_OBJECT.ai.squad!=None:
            WORLD_OBJECT.ai.squad.members.remove(WORLD_OBJECT)    

        # add to this squad
        self.members.append(WORLD_OBJECT)

        # set squad var in ai
        WORLD_OBJECT.ai.squad=self

        # not sure what else we need to do

    #---------------------------------------------------------------------------
    def reset_squad_variable(self):
        # this is called by world builder after it adds the members 
        for b in self.members:
            if b.is_human:
                b.ai.squad=self

    #---------------------------------------------------------------------------
    def update(self):
        pass
          

