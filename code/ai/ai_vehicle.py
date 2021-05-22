
'''
module : ai_vehicle.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import random
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder

# module specific variables
module_version='0.0' #module software version
module_last_update_date='May 21 2021' #date of last update

#global variables

class AIVehicle(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.primary_weapon=None
        self.throwable=None
        self.health=100
        self.ai_state='none'
        self.ai_goal='none'
        self.time_since_ai_transition=0.
        self.ai_think_rate=0
        # the ai group that this human is a part of 
        self.squad=None
        self.target_object=None
        self.destination=None

        # current fuel type options : gas / diesel
        self.fuel_type='gas'
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            print(self.owner.name+' has died')
            for b in self.owner.inventory:
                b.world_coords=[self.owner.world_coords[0]+float(random.randint(-15,15)),self.owner.world_coords[1]+float(random.randint(-15,15))]
                self.owner.world.add_object(b)
            self.owner.world.remove_object(self.owner)

        if self.primary_weapon!=None:
            # needs updates for time tracking and other stuff
            self.primary_weapon.update()

        if self.owner.is_player:
            self.handle_player_update()
        elif self.owner.is_zombie:
            self.handle_zombie_update()
        else :
            self.handle_normal_ai_update()



    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        if EVENT_DATA.is_projectile:
            self.health-=random.randint(25,75)
            engine.world_builder.spawn_blood_splatter(self.owner.world,self.owner.world_coords)
        elif EVENT_DATA.is_grenade:
            print('bonk')

    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):
        if EVENT_DATA.is_gas :
            if self.fuel_type=='gas':
                print('filling up')
            else :
                # put in inventory?
                pass 
        elif EVENT_DATA.is_diesel :
            if self.fuel_type=='diesel':
                print('filling up')
            else : 
                pass 
   
    #---------------------------------------------------------------------------
    def fire(self,TARGET_COORDS):
        ''' fires the (primary?) weapon '''    
        if self.primary_weapon!=None:
            self.primary_weapon.ai.fire(self.owner.world_coords,TARGET_COORDS)

    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if EVENT=='add_inventory':
            self.event_add_inventory(EVENT_DATA)
        elif EVENT=='collision':
            self.event_collision(EVENT_DATA)

    #-----------------------------------------------------------------------
    def handle_normal_ai_think(self):
        ''' normal AI thinking method '''
        # this is basically a thinking state - check the current progress on whatever 
        # the ai thinks it is doing

        # reset transition to zero
        self.time_since_ai_transition=0

        # randomize time before we hit this method again
        self.ai_think_rate=random.uniform(0.1,1.5)

        if self.ai_state=='moving':
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.destination)
            #print('distance: '+str(distance))

            if self.ai_goal=='pickup':
                if distance<5:
                    print('pickup thingy')
                    if self.target_object in self.owner.world.wo_objects:
                        self.owner.add_inventory(self.target_object)
                        self.owner.world.remove_object(self.target_object)
                    else:
                        # hmm object is gone. someone else must have grabbed it
                        print('robbed!!')
                    self.ai_state='sleeping'
            elif self.ai_goal=='close_with_target':
                # check if target is dead 
                if self.target_object.ai.health<1:
                    self.ai_state='sleeping'
                    self.ai_goal='none'
                    self.target_object=None
                elif distance<500:
                    print('in range of target')
                    self.ai_state='engaging'
                    self.ai_goal='none'
                else:
                    # reset the destination coordinates
                    self.ai_goal='close_with_target'
                    self.destination=copy.copy(self.target_object.world_coords)
                    self.ai_state='start_moving'
                    print('close with target')
            else:
                # catchall for random moving related goals:
                if distance<3:
                    self.ai_state='sleeping'
        elif self.ai_state=='engaging':
            # check if target is dead 
            if self.target_object.ai.health<1:
                self.ai_state='sleeping'
                self.ai_goal='none'
                self.target_object=None
            else:
                # check if target is too far 
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.target_object.world_coords)
                if distance >850. :
                    self.ai_goal='close_with_target'
                    self.destination=copy.copy(self.target_object.world_coords)
                    self.ai_state='start_moving'
                    print('closing with target')

            # check if we are out of ammo

        else :
            # what should we be doing ??

            #---- soldier ------------------------------------------------------
            if self.owner.is_soldier :

                # distance from group 
                distance_group=engine.math_2d.get_distance(self.owner.world_coords,self.squad.world_coords)
                
                # are we low on health? 
                if self.health<10:
                    o=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_consumable)
                    if o != None:
                        self.target_object=o
                        self.ai_goal='pickup'
                        self.destination=self.target_object.world_coords
                        self.ai_state='start_moving'  
                    else :
                        # no health to be had. time to run away
                        self.destination=[self.owner.world_coords[0]+float(random.randint(-2300,2300)),self.owner.world_coords[1]+float(random.randint(-2300,2300))]
                        self.ai_state='start_moving'  
                # do we need a gun ?
                elif self.primary_weapon==None :
                    self.target_object=self.owner.world.get_closest_gun(self.owner.world_coords)
                    self.ai_goal='pickup'
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving'
                # do we need ammo ?
                # are we too far from the group?
                elif distance_group >300. :
                    self.ai_goal='close_with_group'
                    self.destination=copy.copy(self.squad.world_coords)
                    self.time_since_ai_transition=0
                    self.ai_state='start_moving'
                    print('getting closer to group')
                else:
                    self.target_object=self.squad.get_enemy()
                    if self.target_object!=None:
                        self.ai_state='engaging'
                        self.ai_goal='none'
                    else:
                        # health is good
                        # weapon is good
                        # we are near the group
                        # there are no enemies to engage
                        # hunt for cheese??
                        # nah lets just wander around a bit
                        self.ai_goal='booored'
                        # soldier gets a much tighter roam distance than civilians
                        self.destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
                        self.ai_state='start_moving'
                        #print('soldier - bored')

            #---- civilian ---------------------------------------------------------------
            else  :

                # are we low on health? 
                if self.health<50:
                    o=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_consumable)
                    if o != None:
                        self.target_object=o
                        self.ai_goal='pickup'
                        self.destination=self.target_object.world_coords
                        self.ai_state='start_moving'  
                    else :
                        # no health to be had. time to run away
                        self.destination=[self.owner.world_coords[0]+float(random.randint(-2300,2300)),self.owner.world_coords[1]+float(random.randint(-2300,2300))]
                        self.ai_state='start_moving'  
                # do we need a gun ?
                elif self.primary_weapon==None :
                    self.target_object=self.owner.world.get_closest_gun(self.owner.world_coords)
                    self.ai_goal='pickup'
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving'
                # do we need ammo ?
                else:
                    # health is good
                    # weapon is good
                    # hunt for cheese??
                    # nah lets just wander around a bit
                    self.ai_goal='booored'
                    self.destination=[self.owner.world_coords[0]+float(random.randint(-300,300)),self.owner.world_coords[1]+float(random.randint(-300,300))]
                    self.ai_state='start_moving'


    #-----------------------------------------------------------------------
    def handle_normal_ai_update(self):
        ''' handle code for civilians and soldiers '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        self.time_since_ai_transition+=time_passed

        if self.time_since_ai_transition>self.ai_think_rate :
            # lets rethink what we are doing
            self.handle_normal_ai_think()
        else:
            # lets not think, just act..
            # if a state isn't in here the AI will basically sleep until the next think

            if self.ai_state=='moving':
                # move towards target
                self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.owner.speed,self.owner.world_coords,self.destination,time_passed)           
            elif self.ai_state=='engaging':
                self.fire(self.target_object.world_coords)
            elif self.ai_state=='sleeping':
                pass
            elif self.ai_state=='start_moving':
                # this kicks off movement
                # maybe change into moving animation image?
                # set the rotation angle for the image 
                self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.destination)
                # transition to moving
                self.time_since_ai_transition=0
                self.ai_state='moving'


    #---------------------------------------------------------------------------
    def handle_player_update(self):
        ''' handle any player specific code'''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        if(self.owner.world.graphic_engine.keyPressed('w')):
            self.owner.world_coords[1]-=self.owner.speed*time_passed
            self.owner.rotation_angle=0
        if(self.owner.world.graphic_engine.keyPressed('s')):
            self.owner.world_coords[1]+=self.owner.speed*time_passed
            self.owner.rotation_angle=180
        if(self.owner.world.graphic_engine.keyPressed('a')):
            self.owner.world_coords[0]-=self.owner.speed*time_passed
            self.owner.rotation_angle=90
        if(self.owner.world.graphic_engine.keyPressed('d')):
            self.owner.world_coords[0]+=self.owner.speed*time_passed
            self.owner.rotation_angle=270
        if(self.owner.world.graphic_engine.keyPressed('f')):
            # fire the gun
            self.fire(self.owner.world.graphic_engine.get_mouse_world_coords())
        if(self.owner.world.graphic_engine.keyPressed('g')):
            # throw throwable object
            self.throw([]) 


