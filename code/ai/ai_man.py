
'''
module : ai_player.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
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
module_last_update_date='Feb 07 2020' #date of last update

#global variables

class AIMan(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.primary_weapon=None
        self.throwable=None
        self.health=100
        self.ai_state='none'
        self.ai_goal='none'
        self.time_since_ai_transition=0.
        # the ai group that this human is a part of 
        self.squad=None
        self.target_object=None
        self.destination=None
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            print('d e d : dead')
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
            print('who throws grenades at people?? Rude!')




    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):
        if EVENT_DATA.is_gun :
            if self.primary_weapon==None:
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
        elif EVENT_DATA.is_grenade :
            if self.throwable==None:
                if self.owner.is_player :
                    self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' equipped ]')
                self.throwable=EVENT_DATA
                EVENT_DATA.ai.equipper=self.owner
            else:
                # drop the current weapon and pick up the new one
                self.throwable.world_coords=copy.copy(self.owner.world_coords)
                self.owner.world.add_object(self.primary_weapon)
                if self.owner.is_player :
                    self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' equipped ]')
                self.throwable=EVENT_DATA
                EVENT_DATA.ai.equipper=self.owner
        if EVENT_DATA.is_consumable:
            self.health+=100
            if self.owner.is_player :
                self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ': You eat the whole cheese wheel ]')


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
    def handle_normal_ai_update(self):
        ''' handle code for civilian AI '''
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        self.time_since_ai_transition+=time_passed

        if self.time_since_ai_transition>2. :
            # this is basically a thinking state - assess current progress
            self.time_since_ai_transition=0

            if self.ai_state=='moving':
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.destination)
                print('distance: '+distance)

                if self.ai_goal=='pickup':
                    if distance<5:
                        print('pickup thingy')
                        self.owner.add_inventory(self.target_object)
                        self.owner.world.remove_object(self.target_object)
                        self.ai_state='sleeping'
                elif self.ai_goale=='close_with_target':
                    if distance<30:
                        print('in range of target')
                        self.owner.ai_state='engaging'
            elif self.ai_state=='engaging':
                # check if target is dead 
                if self.target_object.ai.health<1:
                    self.ai_state='sleeping'
                
                # check if target is too far 
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.target_object.world_coords)
                if distance >50. :
                    self.ai_goal='close_with_target'
                    self.destination=copy.copy(self.target_object.world_coords)
                    self.ai_state='start_moving'

                # check if we are out of ammo

            else :
                # what should we be doing ??

                # are we low on health? 
                if self.health<50:
                    pass
                # do we need a gun ?
                elif self.primary_weapon==None :
                    self.target_object=self.owner.world.get_closest_gun(self.owner.world_coords)
                    self.ai_goal='pickup'
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving'
                # do we need ammo ?
                

                # are we a soldier and are we far from our group?
                if self.owner.is_soldier :
                    distance=engine.math_2d.get_distance(self.owner.world_coords,self.group.world_coords)
                    if distance >100. :
                        self.ai_goal='close_with_group'
                        self.destination=copy.copy(self.group.world_coords)
                        self.time_since_ai_transition=0
                        self.ai_state='start_moving'
                    else:
                        self.target_object=self.squad.get_enemy()
                        if self.target_object!=None:
                            self.ai_state='engaging'
                            self.ai_goal='none'


        if self.ai_state=='moving':
            # move towards target
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.owner.speed,self.owner.world_coords,self.destination,time_passed)           
        elif self.ai_state=='engaging':
            self.fire(self.target_object.world_coords)
        elif self.ai_state=='sleeping':
            pass
        elif self.ai_state=='start_moving':
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

    #---------------------------------------------------------------------------
    def handle_zombie_update(self):
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        if self.health>50:
            self.owner.speed=35
            self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.owner.world.player.world_coords)
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.owner.speed,self.owner.world_coords,self.owner.world.player.world_coords,time_passed)       
        else :
            self.owner.speed=-35
            self.health+=5*time_passed
            self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world.player.world_coords,self.owner.world_coords)
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.owner.speed,self.owner.world_coords,self.owner.world.player.world_coords,time_passed)       
  
    #---------------------------------------------------------------------------
    def throw(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man '''    
        if self.throwable!=None:
            self.throwable.ai.throw(TARGET_COORDS)
            self.owner.world.add_object(self.throwable)
            self.throwable=None
