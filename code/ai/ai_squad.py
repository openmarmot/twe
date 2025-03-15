
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

        self.world=world

        # destination - this is set by the faction tactical ai
        self.destination=[0.,0.]

        # text explanation of current orders 
        #self.current_orders=''
        
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

        # whether the squad is connected to a radio or not
        self.radio_contact=False
        self.last_radio_eval_time=0
        self.radio_eval_rate=0 # updates after first check

        # incoming radio messages go here
        # radio operators will add messages to this queue
        # team leaders will pop them and think about them
        self.radio_receive_queue=[]

        # outgoing messages go here
        # radio operators will pop them and send them through their radios
        self.radio_send_queue=[]
        # format [world.world_seconds,'message']

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

    #---------------------------------------------------------------------------
    def update_radio_contact(self):
        '''checks if the squad is in range of a radio'''
        self.last_radio_eval_time=self.world.world_seconds
        self.radio_eval_rate=random.uniform(1,3.5)

        # reset
        self.radio_contact=False

        # first check each member to see if they are in a vehicle with a radio
        # or have a radio
        for b in self.members:
            if self.radio_contact:
                break

            # check if anyone is in a vehicle with a working radio
            if b.ai.memory['current_task']=='task_vehicle_crew':
                vehicle=b.ai.memory['task_vehicle_crew']['vehicle']
                for c in vehicle.ai.inventory:
                    if c.is_radio:
                        if c.ai.power_on:
                            self.radio_contact=True
                            break

            # check if the bot has a radio in inventory
            for c in b.ai.inventory:
                if c.is_radio:
                    if c.ai.power_on:
                        self.radio_contact=True
                        break

        # next check any radios that are in the world for proximity
        # this is more expensive
        if self.radio_contact==False:
            # unlikely to be very many of these
            for b in self.world.wo_objects_radio:
                if self.radio_contact:
                    break
                for c in self.members:
                    if engine.math_2d.get_distance(b.world_coords,c.world_coords)<200:
                        self.radio_contact=True
                        break

          

