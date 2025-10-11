
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : holds some squad specific variables
most of the logic should be in ai_human
'''


#import built in modules
import random 
import copy

#import custom packages
import engine.math_2d
import engine.log

#global variables

class AISquad(object):
    def __init__(self,world):

        # !! NOTE - this should have as little as possible in it. most stuff should be in ai_human

        self.world=world
        
        # people in the squad 
        # ai_human will remove itself on death 
        self.members=[]

        # vehicles the squad spawned with
        self.vehicles=[]

        # world_object squad member who is the leader.
        # squad memebers will self elect and update this 
        # however if the squad is busy it might take a minute
        self.squad_leader=None

        # faction - german/soviet/american/civilian
        self.faction='none'

        # a link back to the parent faction tactical
        self.faction_tactical=None


        self.name=''

    #---------------------------------------------------------------------------
    def add_to_squad(self, WORLD_OBJECT):
        ''' add a world_object to the squad. DOES NOT SPAWN AT THE MOMENT'''
        if WORLD_OBJECT.is_human:
            # remmove from the old squad
            if WORLD_OBJECT.ai.squad!=None:
                WORLD_OBJECT.ai.squad.members.remove(WORLD_OBJECT)    

            # add to this squad
            self.members.append(WORLD_OBJECT)

            # set squad var in ai
            WORLD_OBJECT.ai.squad=self
        elif WORLD_OBJECT.is_vehicle:
            self.vehicles.append(WORLD_OBJECT)
        else:
            engine.log.add_data('error',f'AISquad.add_to_squad() unknown object type {WORLD_OBJECT.name}',True)
            

    #---------------------------------------------------------------------------
    def reset_squad_variable(self):
        # this is called by world builder after it adds the members 
        for b in self.members:
            if b.is_human:
                b.ai.squad=self

    #---------------------------------------------------------------------------
    def update(self):
        if self.world.world_seconds-self.last_radio_eval_time>self.radio_eval_rate:
            self.update_radio_contact()




          

