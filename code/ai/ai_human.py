
'''
module : ai_player.py
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
module_last_update_date='June 24 2021' #date of last update

#global variables

class AIHuman(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.primary_weapon=None
        self.throwable=None
        self.antitank=None
        self.health=100
        self.bleeding=False
        self.time_since_bleed=0
        self.bleed_interval=0.5

        self.confirmed_kills=0
        self.probable_kills=0

        # what the ai is actually doing (an action)
        self.ai_state='none'
        # what the ai is trying to accomplish
        self.ai_goal='none'

        # the reason the ai jumped in the vehicle
        self.ai_vehicle_goal='none'
        # a destination the ai wants to get to with the vehicle
        self.ai_vehicle_destination=None

        self.time_since_ai_transition=0.
        self.ai_think_rate=0
        # the ai group that this human is a part of 
        self.squad=None
        self.target_object=None
        self.destination=None

        # list of personal enemies the AI has
        # not assigned from squad - mostly assigned through getting shot at the moment 
        self.personal_enemies=[]

        # inventory - for small non-gun objects 
        self.inventory=[]
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            self.handle_death()
        else :
            
            if self.bleeding:
                
                self.time_since_bleed+=self.owner.world.graphic_engine.time_passed_seconds
                if self.time_since_bleed>self.bleed_interval:
                    # make this a bit random 
                    self.bleed_interval=0.5+random.randint(0,20)
                    self.health-=1+random.randint(0,10)
                    self.time_since_bleed=0
                    engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)


            if self.primary_weapon!=None:
                # needs updates for time tracking and other stuff
                self.primary_weapon.update()

            if self.owner.is_player:
                self.handle_player_update()
            else :
                self.handle_normal_ai_update()



    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        if EVENT_DATA.is_projectile:
            self.health-=random.randint(25,75)
            self.bleeding=True
            engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)

            if self.owner.is_player:
                self.owner.world.graphic_engine.text_queue.insert(0,'You are hit and begin to bleed')


            # add the shooter of the bullet to the personal enemies list
            # bullets and shrapnel from grenades and panzerfausts track ownership
            if EVENT_DATA.ai.shooter !=None:
                # this creates a lot of friendly fire - but its interesting 
                self.personal_enemies.append(EVENT_DATA.ai.shooter)

                # let the squad know (this is only until the enemy list is rebuilt)
                # enemy may not be 'near' the rest of the squad - which creates interesting behaviors

                if EVENT_DATA.ai.shooter.ai.squad != None:
                    if EVENT_DATA.ai.shooter.ai.squad.faction != self.squad.faction:
                        self.squad.near_enemies.append(self.personal_enemies[0])

                # kill tracking
                # just focus on humans for now
                if EVENT_DATA.ai.shooter.is_human:
                    if self.health<10:
                        if self.health<1:
                            EVENT_DATA.ai.shooter.ai.confirmed_kills+=1
                        else:
                            EVENT_DATA.ai.shooter.ai.probable_kills+=1
            else:
                print('Error - projectile shooter is none')

        elif EVENT_DATA.is_grenade:
            # not sure what to do here. the grenade explodes too fast to really do anything 
            pass 

        # this is very important because it breaks us out of whatever ai cycle we were in
        # we are put in a very short movement cycle and then the AI can 'think' about what to do next
        self.ai_goal='react to collision'
        self.destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
        self.ai_state='start_moving'

            


    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):

        # add item to inventory no matter what
        self.inventory.append(EVENT_DATA)

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
                self.inventory.remove(self.primary_weapon)
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
                self.owner.world.add_object(self.throwable)
                self.inventory.remove(self.throwable)
                if self.owner.is_player :
                    self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' equipped ]')
                self.throwable=EVENT_DATA
                EVENT_DATA.ai.equipper=self.owner
        elif EVENT_DATA.is_handheld_antitank :
            if self.antitank==None:
                if self.owner.is_player :
                    self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' equipped ]')
                self.antitank=EVENT_DATA
                EVENT_DATA.ai.equipper=self.owner
            else:
                # drop the current weapon and pick up the new one
                self.antitank.world_coords=copy.copy(self.owner.world_coords)
                self.owner.world.add_object(self.antitank)
                self.inventory.remove(self.antitank)
                if self.owner.is_player :
                    self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' equipped ]')
                self.antitank=EVENT_DATA
                EVENT_DATA.ai.equipper=self.owner




    #---------------------------------------------------------------------------
    def fire(self,TARGET_COORDS):
        ''' fires the (primary?) weapon '''    
        if self.primary_weapon!=None:
            self.primary_weapon.ai.fire(self.owner.world_coords,TARGET_COORDS)

    #---------------------------------------------------------------------------
    def handle_death(self):
        # drop inventory 
        for b in self.inventory:
            b.world_coords=[self.owner.world_coords[0]+float(random.randint(-15,15)),self.owner.world_coords[1]+float(random.randint(-15,15))]
            self.owner.world.add_object(b)

        # remove from squad 
        if self.squad != None:
            if self.owner in self.squad.members:
                self.squad.members.remove(self.owner)
            else: 
                # this happens and I do not know why

                print('!! Error : '+self.owner.name+' not in squad somehow')
                print('Squad list')
                for b in self.squad.members:
                    print(b.name)

        self.owner.world.remove_object(self.owner)

        if self.owner.is_player:
            # turn on the player death menu
            self.owner.world.world_menu.active_menu='death'
            self.owner.world.world_menu.menu_state='none'
            # fake input to get the text added
            self.owner.world.world_menu.handle_input('none')

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
            self.think_move()
        elif self.ai_state=='engaging':
            self.think_engage()

        # AI is not in a state that we do anything with. probably sleeping
        else :
            self.think_generic()

                    
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
        if(self.owner.world.graphic_engine.keyPressed('w')):
            self.owner.world_coords[1]-=self.owner.speed*time_passed
            self.owner.rotation_angle=0
            self.owner.reset_image=True
        if(self.owner.world.graphic_engine.keyPressed('s')):
            self.owner.world_coords[1]+=self.owner.speed*time_passed
            self.owner.rotation_angle=180
            self.owner.reset_image=True
        if(self.owner.world.graphic_engine.keyPressed('a')):
            self.owner.world_coords[0]-=self.owner.speed*time_passed
            self.owner.rotation_angle=90
            self.owner.reset_image=True
        if(self.owner.world.graphic_engine.keyPressed('d')):
            self.owner.world_coords[0]+=self.owner.speed*time_passed
            self.owner.rotation_angle=270
            self.owner.reset_image=True
        if(self.owner.world.graphic_engine.keyPressed('f')):
            # fire the gun
            self.fire(self.owner.world.graphic_engine.get_mouse_world_coords())
        if(self.owner.world.graphic_engine.keyPressed('g')):
            # throw throwable object
            self.throw([]) 
        if(self.owner.world.graphic_engine.keyPressed('t')):
            # launch anti tank
            self.launch_antitank([])
        if(self.owner.world.graphic_engine.keyPressed('b')):
            if self.bleeding:
                self.bleeding=False
                self.owner.world.graphic_engine.text_queue.insert(0,'You apply a bandage')


    #---------------------------------------------------------------------------
    def launch_antitank(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man ''' 
        if self.antitank!=None:
            self.antitank.ai.launch(TARGET_COORDS)
            self.owner.world.add_object(self.antitank)
            self.antitank=None

    
    #-----------------------------------------------------------------------
    def think_engage(self):
        ''' think about the current engagement'''
        # check if target is still alive
        if self.target_object.ai.health<1:
            self.ai_state='sleeping'
            self.ai_goal='none'
            self.target_object=None
        else:
            #target is alive, determine the best way to engage
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.target_object.world_coords)
            if distance>300:
                if self.primary_weapon==None:
                    # get a gun 
                    self.target_object=self.owner.world.get_closest_gun(self.owner.world_coords)
                    self.ai_goal='pickup'
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving'
                else:
                    self.think_engage_far(distance)
            else:
                self.think_engage_close(distance)

        # basically if the ai_state doesn't change we will keep firing the next action cycle

    def think_engage_close(self, DISTANCE):
        ''' engagements <301'''
        # if the ai_state isn't changed the gun will be fired on the next action cycle
        if DISTANCE>100:
            # maybe throw a grendate !
            if self.throwable != None:
               self.throw(self.target_object.world_coords)


    #-----------------------------------------------------------------------
    def think_engage_far(self,DISTANCE):
        ''' engagements >301. assumes primary weapon exists. assumes target is alive'''
        # if the ai_state isn't changed the gun will be fired on the next action cycle
        # we have a primary weapon
        # check if we are out of ammo
        if self.primary_weapon.ai.magazine<1 and self.primary_weapon.ai.magazine_count<1:
            # we are out of ammo
            # get more ammo 
            self.target_object=self.owner.world.get_closest_ammo_source(self.owner)
            self.ai_goal='get ammo'
            self.destination=self.target_object.world_coords
            self.ai_state='start_moving'
        else:
            # we have ammo, target is alive

            # check if target is too far 
            if DISTANCE >self.primary_weapon.ai.range :
                self.ai_goal='close_with_target'
                self.destination=copy.copy(self.target_object.world_coords)
                self.ai_state='start_moving'
                #print('closing with target')

    #-----------------------------------------------------------------------
    def think_generic(self):
        ''' when the ai_state doesn't have any specific think actions'''
        # what should we be doing ??

        # 1. are we low on health? 
        if self.health<10:
 
            if self.think_healing_options()==False :
                # no health to be had. time to run away
                self.destination=[self.owner.world_coords[0]+float(random.randint(-2300,2300)),self.owner.world_coords[1]+float(random.randint(-2300,2300))]
                self.ai_state='start_moving'  
        
        # 2. health is good. deal with personal enemies
        elif len(self.personal_enemies)>0:
            # we have a gun, lets make sure this enemy is alive
            #print(self.personal_enemies)
            if self.personal_enemies[0].ai.health>0:
                # engage first personal enemy
                self.target_object=self.personal_enemies[0]
                self.ai_state='engaging'
                self.ai_goal='none'

            else:
                # remove the enemy as it is dead
                self.personal_enemies.pop(0)

        # 3. health is good, no personal enemies 
        else :
            # get an enemy from the squad
            self.target_object=self.squad.get_enemy()
            if self.target_object!=None:
                self.ai_state='engaging'
                self.ai_goal='none'
            else:
                # no enemies, what now?
                # are we too far from the group?
                # distance from group 
                distance_group=engine.math_2d.get_distance(self.owner.world_coords,self.squad.world_coords)
                if distance_group >300. :
                    self.ai_goal='close_with_group'
                    self.destination=copy.copy(self.squad.world_coords)
                    self.time_since_ai_transition=0
                    self.ai_state='start_moving'
                    #print('getting closer to group')
                else:
                    self.think_idle()

    #-----------------------------------------------------------------------
    def think_healing_options(self):
        '''evaluate health options return bool as to whether action is taken'''
        status=False
        # 1 check if we have anything in inventory
        item=None
        for b in self.inventory:
            if b.is_consumable:
                item=b
                break
        if item!=None:
            # consume item. maybe there should be a function for this?
            print('nom nom nom')
            self.inventory.remove(item)
            self.bleeding=False
            self.health+=50
            status=True

        # 2 else check if anything is nearby
        if status==False:
            o=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_consumable)
            if o != None:
                self.target_object=o
                self.ai_goal='pickup'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving'
                status=True
        return status

    #-----------------------------------------------------------------------
    def think_idle(self):
        ''' think about low priority actions to do '''
        # no enemies
        # health is fine
        # close to group

        # check if we can upgrade gear
        if self.think_upgrade_gear()==False:
            # we didn't upgrade gear. what should we do ?
            # hunt for cheese??
            # nah lets just wander around a bit
            self.ai_goal='booored'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-300,300)),self.owner.world_coords[1]+float(random.randint(-300,300))]
            self.ai_state='start_moving'


    #-----------------------------------------------------------------------
    def think_move(self):
        ''' think about the current movement'''
        distance=engine.math_2d.get_distance(self.owner.world_coords,self.destination)

        # should we get a vehicle instead of hoofing it to wherever we are going?
        if distance>2000:
            b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_vehicle)
            if b!=None:
                v_distance=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)

                # only bother with a vehicle if it will be faster
                if v_distance<distance:

                    # head towards the vehicle
                    # should check if the vehicle is hostile

                    self.ai_vehicle_goal='travel'
                    self.ai_vehicle_destination=copy.copy(self.destination)

                    self.target_object=b
                    self.ai_goal='enter object'
                    # not using copy here because vehicle may move
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving'

                    print(self.owner.name + ' heading towards '+b.name+' distance: '+str(distance))
                else :
                    # guess we might as well walk
                    pass

            else:
                # no vehicles ?
                pass
        else:
            # ai_state=='moving AND distance <1000
            if self.ai_goal=='pickup':
                if distance<5:
                    if self.target_object in self.owner.world.wo_objects:
                        self.owner.add_inventory(self.target_object)
                        self.owner.world.remove_object(self.target_object)
                    else:
                        # hmm object is gone. someone else must have grabbed it
                    # print('robbed!!')
                        pass
                    self.ai_state='sleeping'
            elif self.ai_goal=='enter object':

                # vehicles move around a lot so gotta check
                if self.destination!=self.target_object.world_coords:
                    self.destination=copy.copy(self.target_object.world_coords)
                    self.ai_state='start_moving'
                else:
                    if distance<5:
                        if self.target_object in self.owner.world.wo_objects:
                            self.target_object.add_inventory(self.owner)
                            self.owner.world.remove_object(self.owner)
                            print(self.owner.name+' entered '+ self.target_object.name)

                        else:
                            # hmm object is gone. idk how that happened
                            print('object I was going to enter disappeared')
                            pass
                        self.ai_state='sleeping'
            elif self.ai_goal=='get ammo':
                if distance<5:
                    print('replenishing ammo ')
                    # get max count of fully loaded magazines
                    self.primary_weapon.ai.magazine_count=self.primary_weapon.ai.max_magazines
                    self.ai_state='sleeping'
            elif self.ai_goal=='close_with_target':
                # check if target is dead 
                if self.target_object.ai.health<1:
                    self.ai_state='sleeping'
                    self.ai_goal='none'
                    self.target_object=None
                elif distance<self.primary_weapon.ai.range:
                    #print('in range of target')
                    self.ai_state='engaging'
                    self.ai_goal='none'
                else:
                    # reset the destination coordinates
                    self.ai_goal='close_with_target'
                    self.destination=copy.copy(self.target_object.world_coords)
                    self.ai_state='start_moving'
                # print('close with target')
            else:
                # catchall for random moving related goals:
                if distance<3:
                    self.ai_state='sleeping'

    #-----------------------------------------------------------------------
    def think_upgrade_gear(self):
        '''think about upgrading gear. return True/False if upgrading'''
        status=False
        # grab another grenade?
        if self.throwable == None:
            b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_grenade)
            if b != None:
                d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)
                # make sure its close - we don't want to wander far from the group
                if d<400:
                    status=True
                    self.target_object=b
                    self.ai_goal='pickup'
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving' 

        # upgrade weapon?
        if status==False:
            if self.primary_weapon!=None:
                if self.primary_weapon.ai.type=='pistol' or self.primary_weapon.ai.type=='rifle':
                    b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns)
                    if b != None:
                        # the thought here being that riles are undesirable, and a mg is crew served and unlikely to 
                        # be picked up
                        if b.ai.type=='submachine gun' or b.ai.type=='assault rifle':
                            d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)
                            # make sure its close - we don't want to wander far from the group
                            if d<500:
                                status=True
                                self.target_object=b
                                self.ai_goal='pickup'
                                self.destination=self.target_object.world_coords
                                self.ai_state='start_moving' 
                                print('swapping '+self.primary_weapon.name + 'for '+b.name)

            else:
                # could get a weapon - but maybe everything doesn't need one ??
                pass

        # upgrade clothes / armor

        # top off ammo ?

        return status
    #---------------------------------------------------------------------------
    def throw(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man '''    
        if self.throwable!=None:
            self.throwable.ai.throw(TARGET_COORDS)
            self.owner.world.add_object(self.throwable)
            self.throwable=None
