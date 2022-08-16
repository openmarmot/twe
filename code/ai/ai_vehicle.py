
'''
module : ai_vehicle.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : a lot of this code came from ai_human but it has diverged a bit
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
module_last_update_date='July 09 2021' #date of last update

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

        # passengers[0] determines how the AI is controlled
        self.passengers=[]

        # 
        self.inventory=[]

        # actual vehicle speed
        self.vehicle_speed=0.
        self.acceleration=0
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            print(self.owner.name+' has died')
            engine.world_builder.spawn_container('cat',self.owner.world,self.owner.world_coords,self.owner.rotation_angle,self.owner.image_list[1],self.inventory)

            # dump passengers
            for b in self.passengers:
                b.world_coords=[self.owner.world_coords[0]+float(random.randint(-15,15)),self.owner.world_coords[1]+float(random.randint(-15,15))]
                self.owner.world.add_object(b)

            self.owner.world.remove_object(self.owner)

        if self.primary_weapon!=None:
            # needs updates for time tracking and other stuff
            self.primary_weapon.update()


        if len(self.passengers)>0:
            if self.passengers[0].is_player:
                self.handle_player_update()
            else :
                self.handle_normal_ai_update()

            # update passenger coords 
            # this fixes a lot of other weirdness 
            for b in self.passengers:
                b.world_coords=copy.copy(self.owner.world_coords)



    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        if EVENT_DATA.is_projectile:
            self.health-=random.randint(3,15)
            engine.world_builder.spawn_object(self.owner.world,EVENT_DATA.world_coords,'dirt',True)

        elif EVENT_DATA.is_grenade:
            print('bonk')

    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):

        if EVENT_DATA.is_human:
            if EVENT_DATA.is_player:
                self.owner.is_player=True
                # passengers[0] controls the vehicle so put player there
                self.passengers.insert(0,EVENT_DATA)
            else:
                # don't care about NPCs, place them anywhere
                self.passengers.append(EVENT_DATA)
        else:
            if EVENT_DATA.is_gun :
                if self.primary_weapon==None:
                    self.inventory.append(EVENT_DATA)
                    if self.owner.is_player :
                        self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' equipped ]')
                    self.primary_weapon=EVENT_DATA
                    EVENT_DATA.ai.equipper=self.owner
                else:
                    # drop the current weapon and pick up the new one
                    self.primary_weapon.world_coords=copy.copy(self.owner.world_coords)
                    self.owner.world.add_object(self.primary_weapon)
                    if self.owner.is_player :
                        self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' equipped ]')
                    self.primary_weapon=EVENT_DATA
                    EVENT_DATA.ai.equipper=self.owner
            elif EVENT_DATA.is_gas :
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
            else:
                self.inventory.append(EVENT_DATA) 


    #---------------------------------------------------------------------------
    def event_remove_inventory(self,EVENT_DATA):
        if EVENT_DATA.is_human:
            EVENT_DATA.world_coords=copy.copy(self.owner.world_coords)
            self.passengers.remove(EVENT_DATA)
            if EVENT_DATA.is_player:
                self.owner.is_player=False
        else:
            if EVENT_DATA in self.inventory:

                # make sure the obj world_coords reflect the obj that had it in inventory
                EVENT_DATA.world_coords=copy.copy(self.owner.world_coords)

                self.inventory.remove(EVENT_DATA)

                if self.primary_weapon==EVENT_DATA:
                    self.primary_weapon=None

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
        elif EVENT=='remove_inventory':
            self.event_remove_inventory(EVENT_DATA)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+EVENT)

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

            if self.ai_goal=='drop off passenger':
                if distance<30:
                    print('dropping off passenger')

                    b=self.passengers.pop(0)
                    b.wo_start()
                    print('dropped off '+b.name)
                    self.ai_state='sleeping'
            else:
                # catchall for random moving related goals:
                # distance fuzzyness should be higher because the vehicle is more inexact
                if distance<20:
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
            # lets see what the passengers want to do

            # would be better to sort passengers and drop off the closest
            if self.passengers[0].ai.ai_vehicle_goal=='travel':
                self.ai_goal='drop off passenger'
                self.destination=copy.copy(self.passengers[0].ai.ai_vehicle_destination)
                self.ai_state='start_moving'




    #-----------------------------------------------------------------------
    def handle_normal_ai_update(self):
        ''' handle code for civilians and soldiers '''
        # this is what the bot does when it isn't thinking 
        # basically mindlessly carries on whatever task it is doing 
        # if there is something that should be decided it goes in handle_normal_ai_think

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

                # tell graphics engine to redo the image 
                self.owner.reset_image=True
                # transition to moving
                self.time_since_ai_transition=0
                self.ai_state='moving'


    #---------------------------------------------------------------------------
    def handle_player_update(self):
        ''' handle any player specific code'''

        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        self.owner.world_coords=engine.math_2d.moveAlongVector(self.vehicle_speed,self.owner.world_coords,self.owner.heading,time_passed)
        #print('speed: '+str(self.vehicle_speed))

        if(self.owner.world.graphic_engine.keyPressed('w')):
            if self.vehicle_speed<self.owner.speed:
                self.vehicle_speed+=self.acceleration*time_passed
                if self.vehicle_speed<10 and self.vehicle_speed>0:
                    self.vehicle_speed=10

        if(self.owner.world.graphic_engine.keyPressed('s')):
            if self.vehicle_speed>self.owner.speed*-1:
                self.vehicle_speed-=self.acceleration*time_passed
                if self.vehicle_speed>-10 and self.vehicle_speed<0:
                    self.vehicle_speed=-10

        if(self.owner.world.graphic_engine.keyPressed('a')):
            self.owner.rotation_angle+=self.owner.rotation_speed*time_passed
            self.owner.heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
            self.owner.reset_image=True

        if(self.owner.world.graphic_engine.keyPressed('d')):
            self.owner.rotation_angle-=self.owner.rotation_speed*time_passed
            self.owner.heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
            self.owner.reset_image=True

            # -- deceleration --
        if self.vehicle_speed>5:
            self.vehicle_speed-=5*time_passed
        elif self.vehicle_speed<-5:
            self.vehicle_speed+=5*time_passed
        elif self.vehicle_speed<9 and self.vehicle_speed>-9:
            self.vehicle_speed=0

        if(self.owner.world.graphic_engine.keyPressed('f')):
            # fire the gun
            self.fire(self.owner.world.graphic_engine.get_mouse_world_coords())
        #if(self.owner.world.graphic_engine.keyPressed('g')):
            # throw throwable object
        #    self.throw([]) 


        # -- normalize angles --
        if self.owner.rotation_angle>360:
            self.owner.rotation_angle=0

        elif self.owner.rotation_angle<0:
            self.owner.rotation_angle=360




