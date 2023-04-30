
'''
module : ai_player.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
event - something that could happen to the ai, possibly caused by external forces
handle_SOMETHING - something that the AI decides to do
take_action_ - something that sets ai_state and ai_goal to start an action
think_ - something that requires logic code
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
        self.melee=None
        # objects that are large_human_pickup. only one at a time
        self.large_pickup=None
        self.health=100
        self.bleeding=False
        self.time_since_bleed=0
        self.bleed_interval=0.5

        self.confirmed_kills=0
        self.probable_kills=0

        # a description of whatever collided with this object last. 
        self.last_collision_description=''

        # what the ai is actually doing (an action)
        self.ai_state='none'
        # what the ai is trying to accomplish
        self.ai_goal='none'

        # a lot of these are reset by event_add_inventory()
        self.ai_want_gun=False
        self.ai_want_gun_upgrade=False
        self.ai_want_grenade=False
        self.ai_want_antitank=False
        self.ai_want_ammo=False
        self.ai_want_food=False
        self.ai_want_drink=False
        self.ai_want_medical=False
        self.ai_want_cover=False




        self.in_vehicle=False
        # the vehicle the ai is in
        self.vehicle=None
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

        # fatigue is used as a modifier for a bunch of stuff
        # doing things adds fatigue, it slowly drains away when you aren't moving
        self.fatigue=0
        self.fatigue_add_rate=1
        self.fatigue_remove_rate=0.75

        self.hunger=0
        self.hunger_rate=0.1
        self.thirst=0
        self.thirst_rate=0.1

        # burst control keeps ai from shooting continuous streams
        self.current_burst=0 # int number of bullets shot in current burst
        self.max_burst=10

        # list of personal enemies the AI has
        # not assigned from squad - mostly assigned through getting shot at the moment 
        self.personal_enemies=[]

        self.inventory=[]

        self.missions=[]
        # a mission is a list in the following syntax ['action',target]
        # action : move/kill/pickup/despawn
        # target : either a coordinate or more often a world_object. dependent on the action
        # a mission takes priority over some other actions like following a squad
        # missions will be done in order, making it a sort of programming language for the bots

        # used to prevent repeats
        self.last_speak=''

        # ai takes over if the player is afk
        self.time_since_player_interact=0
        self.time_before_afk=180

        self.speed = 0.
        self.rotation_speed=0.

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            self.handle_death()
        else :

            if self.in_vehicle:
                if self.vehicle.ai.health<1:
                    #this needs to be here as there will exactly one update cycle if a vehicle dies
                    self.handle_vehicle_died()
            
            if self.bleeding:
                
                self.time_since_bleed+=self.owner.world.graphic_engine.time_passed_seconds
                if self.time_since_bleed>self.bleed_interval:
                    # make this a bit random 
                    self.bleed_interval=0.5+random.randint(0,20)
                    self.health-=1+random.randint(0,10)
                    self.time_since_bleed=0
                    engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'small_blood',True)

            if self.primary_weapon!=None:
                # needs updates for time tracking and other stuff
                self.primary_weapon.update()

            # hunger/thirst stuff
            self.hunger+=self.hunger_rate*self.owner.world.graphic_engine.time_passed_seconds
            self.thirst+=self.thirst_rate*self.owner.world.graphic_engine.time_passed_seconds

            if self.owner.is_player:
                self.handle_player_update()
            else :
                self.handle_normal_ai_update()

    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        self.last_collision_description=''
        if EVENT_DATA.is_projectile:
            self.last_collision_description='hit by a projectile '
            starting_health=self.health
            self.health-=random.randint(25,75)
            self.bleeding=True
            engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)

            self.speak('react to being shot')

            if self.owner.is_player:
                self.owner.world.graphic_engine.text_queue.insert(0,'You are hit and begin to bleed')

            # add the shooter of the bullet to the personal enemies list
            # bullets and shrapnel from grenades and panzerfausts track ownership
            if EVENT_DATA.ai.shooter !=None:
                self.last_collision_description+=('from '+EVENT_DATA.ai.shooter.name)
                # this creates a lot of friendly fire - but its interesting 
                self.personal_enemies.append(EVENT_DATA.ai.shooter)

                # let the squad know (this is only until the enemy list is rebuilt)
                # enemy may not be 'near' the rest of the squad - which creates interesting behaviors

                if EVENT_DATA.ai.shooter.ai.squad != None:
                    if EVENT_DATA.ai.shooter.ai.squad.faction != self.squad.faction or EVENT_DATA.ai.shooter.is_player:
                        self.squad.near_enemies.append(self.personal_enemies[0])

                # kill tracking
                # just focus on humans for now
                if EVENT_DATA.ai.shooter.is_human:
                    if self.health<30:
                        # protects from recording hits on something that was already dead
                        if starting_health>0:
                            if self.health<1:
                                EVENT_DATA.ai.shooter.ai.confirmed_kills+=1
                            else:
                                EVENT_DATA.ai.shooter.ai.probable_kills+=1
                        else:
                            print('collision on a dead human ai detected')

                    if EVENT_DATA.ai.shooter.ai.primary_weapon!=None:
                        self.last_collision_description+=("'s "+EVENT_DATA.ai.weapon_name)
            else:
                print('Error - projectile shooter is none')

            if self.owner.is_civilian:
                # civilian runs further
                self.ai_goal='react to collision'
                self.destination=[self.owner.world_coords[0]+float(random.randint(-560,560)),self.owner.world_coords[1]+float(random.randint(-560,560))]
                self.ai_state='start_moving'
            else:
                # soldier just repositions
                self.ai_goal='react to collision'
                self.destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
                self.ai_state='start_moving'

        elif EVENT_DATA.is_grenade:
            # not sure what to do here. the grenade explodes too fast to really do anything

            # attempt to throw the grenade back
            if random.randint(1,5)==1:
                EVENT_DATA.ai.redirect(EVENT_DATA.ai.equipper.world_coords)
            else:
                self.ai_goal='react to collision'
                self.destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
                self.ai_state='start_moving'

        else:
            print('unidentified collision')

            # this is very important because it breaks us out of whatever ai cycle we were in
            # we are put in a very short movement cycle and then the AI can 'think' about what to do next
            self.ai_goal='react to collision'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
            self.ai_state='start_moving'

    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):
        ''' add object to inventory'''
        # in this case EVENT_DATA is a world_object
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
            self.ai_want_gun=False
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
            self.ai_want_grenade=False
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
            self.ai_want_antitank=False
        elif EVENT_DATA.is_large_human_pickup :
            if self.large_pickup==None:
                if self.owner.is_player :
                    self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' picked up ]')
                self.large_pickup=EVENT_DATA
                #EVENT_DATA.ai.equipper=self.owner
            else:
                # drop the current weapon and pick up the new one
                self.large_pickup.world_coords=copy.copy(self.owner.world_coords)
                self.owner.world.add_object(self.large_pickup)
                self.inventory.remove(self.large_pickup)
                if self.owner.is_player :
                    self.owner.world.graphic_engine.text_queue.insert(0,'[ '+EVENT_DATA.name + ' picked up ]')
                self.large_pickup=EVENT_DATA
                EVENT_DATA.ai.equipper=self.owner
        elif EVENT_DATA.is_consumable:
            self.ai_want_food=False
        elif EVENT_DATA.is_liquid_container:
            # this is terrible as this could be non consumable
            self.ai_want_drink=False
        elif EVENT_DATA.is_medical:
            self.ai_want_medical=False

    #---------------------------------------------------------------------------
    def event_remove_inventory(self,EVENT_DATA):
        ''' remove object from inventory '''

        if EVENT_DATA in self.inventory:

            # make sure the obj world_coords reflect the obj that had it in inventory
            EVENT_DATA.world_coords=copy.copy(self.owner.world_coords)

            self.inventory.remove(EVENT_DATA)

            if self.primary_weapon==EVENT_DATA:
                self.primary_weapon=None
            elif self.throwable==EVENT_DATA:
                self.throwable=None
            elif self.antitank==EVENT_DATA:
                self.antitank=None
            elif self.large_pickup==EVENT_DATA:
                self.large_pickup=None

            # need to add a method call here that will search inventory and add new weapon/grendade/whatever if available

        else:
            print('removal error - object not in inventory',EVENT_DATA.name)

    #---------------------------------------------------------------------------
    def fire(self,TARGET_COORDS,WEAPON):
        ''' fires a weapon '''    

        if WEAPON.ai.fire(self.owner.world_coords,TARGET_COORDS):
            self.current_burst+=1

        if self.current_burst>self.max_burst:
            # stop firing, give the ai a chance to rethink and re-engage
            self.current_burst=0
            self.ai_state='sleeping'
            self.ai_goal='none'
            self.target_object=None

    #---------------------------------------------------------------------------
    def get_calculated_speed(self):
        calc_speed=self.speed
        if self.fatigue<3:
            calc_speed*=1.5
        if self.fatigue>5:
            calc_speed*=0.95
        if self.fatigue>10:
            calc_speed*=0.9
        if self.fatigue>20:
            calc_speed*=0.9
        if self.fatigue>30:
            calc_speed*=0.9
        
        return calc_speed
    
    #---------------------------------------------------------------------------
    def handle_change_vehicle_role(self,ROLE):
        ''' change your role on the vehicle crew'''
        # ROLE : driver , gunner, passenger, none
        if self.in_vehicle:

            # remove from existing roles
            if self.vehicle.ai.gunner==self.owner:
                self.vehicle.ai.gunner=None
                if self.vehicle.ai.primary_weapon!=None:
                    self.vehicle.ai.primary_weapon.ai.equipper=None
            if self.vehicle.ai.driver==self.owner:
                self.vehicle.ai.driver=None

            if ROLE=='driver':
                if self.vehicle.ai.driver!=self.owner.world.player:
                    self.vehicle.ai.driver=self.owner
                    self.speak("Taking over driving")
                    
            elif ROLE=='gunner':
                if self.vehicle.ai.gunner!=self.owner.world.player:
                    self.vehicle.ai.gunner=self.owner

                    if self.vehicle.ai.primary_weapon!=None:
                        self.vehicle.ai.primary_weapon.ai.equipper=self.owner

                    self.speak("Taking over gunner position")

            elif ROLE=='passenger':
                # nothing to do here, roles already removed
                pass

        else: 
            print('error: attempting to change vehicle role when not in vehicle')


    #---------------------------------------------------------------------------
    def handle_death(self):
        dm=''
        dm+=(self.owner.name+' died.')
        dm+=('\n  - faction: '+self.squad.faction)
        dm+=('\n  - confirmed kills: '+str(self.confirmed_kills))
        dm+=('\n  - killed by : '+self.last_collision_description)
        print(dm)

        # drop inventory 
        #for b in self.inventory:
         #   b.world_coords=[self.owner.world_coords[0]+float(random.randint(-15,15)),self.owner.world_coords[1]+float(random.randint(-15,15))]
         #   self.owner.world.add_object(b)

        # drop primary weapon 
        if self.primary_weapon!=None:
            self.inventory.remove(self.primary_weapon)
            self.primary_weapon.world_coords=[self.owner.world_coords[0]+float(random.randint(-15,15)),self.owner.world_coords[1]+float(random.randint(-15,15))]
            self.owner.world.add_object(self.primary_weapon)

        # remove from squad 
        if self.squad != None:
            if self.owner in self.squad.members:
                self.squad.members.remove(self.owner)
            else: 
                # haven't had this happen in awhile. must be fixed

                print('!! Error : '+self.owner.name+' not in squad somehow')
                print('Squad list')
                for b in self.squad.members:
                    print(b.name)

        

        # spawn body
        engine.world_builder.spawn_container('body',self.owner.world,self.owner.world_coords,self.owner.rotation_angle,self.owner.image_list[2],self.inventory)

        self.owner.world.remove_object(self.owner)

        if self.owner.is_player:
            # turn on the player death menu
            self.owner.world.world_menu.active_menu='death'
            self.owner.world.world_menu.menu_state='none'
            # fake input to get the text added
            self.owner.world.world_menu.handle_input('none')

    #---------------------------------------------------------------------------
    def handle_drink(self,LIQUID_CONTAINER):
        #LIQUID_CONTAINER world object with ai_liquid_container
        if LIQUID_CONTAINER.ai.used_volume>0:
            if LIQUID_CONTAINER.ai.used_volume>1:
                LIQUID_CONTAINER.ai.used_volume-=1;
            else:
                # <1 liter left. just drink it all
                LIQUID_CONTAINER.ai.used_volume=0

            self.health+=LIQUID_CONTAINER.ai.health_effect
            self.hunger+=LIQUID_CONTAINER.ai.hunger_effect
            self.thirst+=LIQUID_CONTAINER.ai.thirst_effect
            self.fatigue+=LIQUID_CONTAINER.ai.fatigue_effect

            self.speak('drinking some '+LIQUID_CONTAINER.ai.liquid_type)

            # somehow this killed us. add a death description
            if self.health<1:
                self.last_collision_description = 'over consumption of '+LIQUID_CONTAINER.ai.liquid_type

    #---------------------------------------------------------------------------
    def handle_eat(self,CONSUMABLE):
        # eat the consumable object. or part of it anyway
        self.health+=CONSUMABLE.ai.health_effect
        self.hunger+=CONSUMABLE.ai.hunger_effect
        self.thirst+=CONSUMABLE.ai.thirst_effect
        self.fatigue+=CONSUMABLE.ai.fatigue_effect

        self.event_remove_inventory(CONSUMABLE)

    #---------------------------------------------------------------------------
    def handle_enter_vehicle(self,VEHICLE):
        # should maybe pick driver or gunner role here

        VEHICLE.ai.passengers.append(self.owner)
        self.owner.world.remove_object(self.owner)
        self.in_vehicle=True
        self.vehicle=VEHICLE

        if self.owner.is_player or self.vehicle.ai.driver==None:
            self.handle_change_vehicle_role('driver')
        else:
            # not driver, how about gunner?
            if self.vehicle.ai.gunner==None:
                self.handle_change_vehicle_role('gunner')


    #---------------------------------------------------------------------------
    def handle_exit_vehicle(self):
        self.in_vehicle=False
        self.vehicle.ai.passengers.remove(self.owner)
        self.owner.world.add_object(self.owner)
        # remove self from any vehicle roles
        self.handle_change_vehicle_role('none')
        self.vehicle=None
        self.ai_goal='none'
        self.ai_state='none'
        
        self.speak('Jumping out')

    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # this is supposed to be the main interface that the outside world uses to interact with the ai
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

        if self.in_vehicle:
            self.think_in_vehicle()
        elif self.ai_state=='moving':
            self.think_move()
        elif self.ai_state=='engaging':
            self.think_engage()

        # AI is not in a state that we do anything with. probably sleeping
        else :
            self.think_generic()

        # this should be last to over ride the other things we were going to do
        if self.health<10: 
            if self.think_healing_options()==False :
                # no health to be had! (probably impossible with the amount of consumables)
                # roll to see if we panic
                if random.randint(1,5)==1:
                    self.take_action_panic()
  
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
                self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.get_calculated_speed(),self.owner.world_coords,self.destination,time_passed)
                self.fatigue+=self.fatigue_add_rate*time_passed           
            elif self.ai_state=='engaging':
                # wondering if we can remove this if statement
                if self.primary_weapon!=None:
                    self.fire(self.target_object.world_coords,self.primary_weapon)
                else:
                    print('warning: attempt to fire with no primary weapon')
                self.fatigue+=self.fatigue_add_rate*time_passed
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
            elif self.ai_state=='vehicle_drive':
                pass
            else:
                # sleeping or whatever 
                self.fatigue-=self.fatigue_remove_rate*time_passed


    #---------------------------------------------------------------------------
    def handle_player_update(self):
        ''' handle any player specific code'''
        #print('time since player interact ',self.time_since_player_interact)
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        if self.in_vehicle:


            if(self.owner.world.graphic_engine.keyPressed('w')):
                self.vehicle.ai.throttle=1
                self.vehicle.ai.brake_power=0

            if(self.owner.world.graphic_engine.keyPressed('s')):
                self.vehicle.ai.brake_power=1
                self.vehicle.ai.throttle=0

            if(self.owner.world.graphic_engine.keyPressed('a')):
                self.vehicle.ai.handle_steer_left()

            if(self.owner.world.graphic_engine.keyPressed('d')):
                self.vehicle.ai.handle_steer_right()

            if(self.owner.world.graphic_engine.keyPressed('f')):
                #print('pew!')
                # fire the gun
                if self.vehicle.ai.gunner==self.owner:
                    if self.vehicle.ai.primary_weapon!=None:
                        self.fire(self.owner.world.graphic_engine.get_mouse_world_coords(),self.vehicle.ai.primary_weapon)
                    else:
                        print('no vehicle weapon')
                        # fire our own weapon
                        if self.primary_weapon!=None:
                            self.fire(self.owner.world.graphic_engine.get_mouse_world_coords(),self.primary_weapon)
                        else:
                            print('no vehicle gun, no personal gun')
                else:
                    print('you arent the gunner!')


        else:
            action=False
            if(self.owner.world.graphic_engine.keyPressed('w')):
                self.owner.world_coords[1]-=self.speed*time_passed
                self.owner.rotation_angle=0
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('s')):
                self.owner.world_coords[1]+=self.speed*time_passed
                self.owner.rotation_angle=180
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('a')):
                self.owner.world_coords[0]-=self.speed*time_passed
                self.owner.rotation_angle=90
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('d')):
                self.owner.world_coords[0]+=self.speed*time_passed
                self.owner.rotation_angle=270
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('f')):
                # fire the gun
                if self.primary_weapon!=None:
                    self.fire(self.owner.world.graphic_engine.get_mouse_world_coords(),self.primary_weapon)
                action=True
            if(self.owner.world.graphic_engine.keyPressed('g')):
                # throw throwable object
                self.throw([]) 
                action=True
            if(self.owner.world.graphic_engine.keyPressed('t')):
                # launch anti tank
                self.launch_antitank([])
                action=True
            if(self.owner.world.graphic_engine.keyPressed('b')):
                if self.bleeding:
                    self.bleeding=False
                    self.speak('bandage')
                    action=True
            
            if action:
                self.fatigue+=self.fatigue_add_rate*time_passed
                self.time_since_player_interact=0
            else:
                if self.fatigue>0:
                    self.fatigue-=self.fatigue_remove_rate*time_passed

                self.time_since_player_interact+=time_passed
                if self.time_since_player_interact>self.time_before_afk:
                    self.handle_normal_ai_update()

    #-----------------------------------------------------------------------
    def handle_vehicle_died(self):
        if self.in_vehicle:
            self.handle_exit_vehicle()
            self.take_action_move_short_random_distance()
        else:
            print('error: handle vehicle died, but ai not in vehicle')

    #-----------------------------------------------------------------------
    def handle_use_medical_object(self,MEDICAL):
        # MEDICAL - list of is_medical World Object(s)

        # should eventually handle bandages, morphine, etc etc
        # probably need attributes similar to consumables

        # should select the correct medical item to fix whatever the issue is
        selected = MEDICAL[0]
        self.speak('Using medical '+selected.name)

        self.bleeding=False

        self.health+=selected.ai.health_effect
        self.hunger+=selected.ai.hunger_effect
        self.thirst_rate+=selected.ai.thirst_effect
        self.fatigue+=selected.ai.fatigue_effect

        self.event_remove_inventory(selected)

    #---------------------------------------------------------------------------
    def launch_antitank(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man ''' 
        if self.antitank!=None:
            self.antitank.ai.launch(TARGET_COORDS)
            self.owner.world.add_object(self.antitank)
            self.inventory.remove(self.antitank)
            self.antitank=None


    #---------------------------------------------------------------------------
    def speak(self,WHAT):
        ''' say something if the ai is close to the player '''

        # simple way of preventing repeats
        if WHAT !=self.last_speak:
            self.last_speak=WHAT
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            if distance<400:
                s='['+self.owner.name+'] '

                if WHAT=='status':
                    s+=' '+self.ai_state+' '+self.ai_goal
                elif WHAT=='bandage':
                    s+=' applying bandage'
                elif WHAT=='joined squad':
                    s+=' joined squad'
                elif WHAT=='react to being shot':
                    s+=" Aagh! I'm hit !!"
                elif WHAT=='scream':
                    s+='Aaaaaaaaaaaah!!!'
                else:
                    s+=WHAT

                self.owner.world.graphic_engine.add_text(s)


    #-----------------------------------------------------------------------
    def react_asked_to_join_squad(self,SQUAD):
        if SQUAD==self.squad:
            self.speak("I'm already in that squad")
        else:
            if SQUAD.faction==self.squad.faction:
                # yes - lets join this squad 

                SQUAD.add_to_squad(self.owner)
                self.speak('joined squad')
            else:
                self.speak('no')

    #-----------------------------------------------------------------------
    def react_asked_to_upgrade_gear(self):
        status = self.think_upgrade_gear()
        if status :
            self.speak('going to upgrade my gear')
        else:
            self.speak('nothing better than what i got')


    #-----------------------------------------------------------------------
    def take_action_get_ammo(self,NEAR):
        '''attempts to get ammo. returns True/False if it is successful'''

        # preference for ammo
        # 1 - ammo can
        # 2 - squad mate
        # 3 - ???

        # NEAR (bool) - keep distance to 500
        distance=2000
        if NEAR:
            distance=500
        
        best_ammo_can=self.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_ammo_container,distance)
        
        if best_ammo_can!=None:
            self.target_object=best_ammo_can
            self.ai_goal='get ammo'
            self.destination=self.target_object.world_coords
            self.ai_state='start_moving'
            return True
        else:
            # do we have a squad buddy?
            best_squad_mate=None 
            if self.squad != None:
                if len(self.squad.members)>0:
                    best_squad_mate=self.get_closest_object(self.owner.world_coords,self.squad.members,distance)

            if best_squad_mate != None:
                self.target_object=best_ammo_can
                self.ai_goal='get_ammo'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving'
                return True
            else: 
                # curious how often this happens
                print('warn - bot could not find ammo')
                return False

    #-----------------------------------------------------------------------
    def take_action_get_gun(self,NEAR,UPGRADE_ONLY):
        ''' attempts to get a gun. returns True/False if it is successful'''

        # thought - maybe the inventory add for guns should do the gun comparison instead of having it here

        # upgrade logic shoul be broken off into a think_ function and then this can be 
        # merged with take_action_get_item

        # NEAR : only look at guns in 500 range
        # UPGRADE_ONLY : only pickup a better gun (if you already have a gun)
        gun=None

        # NEAR (bool) - keep distance to 500
        distance=2000
        if NEAR:
            distance=500

        gun=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns,distance)

        if gun==None:
            return False
        else:
            if UPGRADE_ONLY and self.primary_weapon!=None:
                if self.primary_weapon.ai.type=='pistol' or self.primary_weapon.ai.type=='rifle':
                    # the thought here being that riles are undesirable, and a mg is crew served and unlikely to 
                    # be picked up
                    if gun.ai.type=='submachine gun' or gun.ai.type=='assault rifle':
                        self.take_action_pickup_object(gun)
                        return True
                    else:
                        return False
            else:
                self.take_action_pickup_object(gun)
                return True
            
#-----------------------------------------------------------------------
    def take_action_get_item(self,NEAR,WORLD_ITEM_LIST):
        ''' attempts to get a item from a list of items. returns True/False if it is successful'''
        # NEAR : (bool) - keep distance to 500
        # WORLD_ITEM_LIST world.wo_object list or any list of world objects
        item=None

        distance=2000
        if NEAR:
            distance=500
        
        item=self.owner.world.get_closest_object(self.owner.world_coords,WORLD_ITEM_LIST,distance) 

        if item==None:
            return False
        else:
            self.take_action_pickup_object(item)
            return True

    #-----------------------------------------------------------------------
    def take_action_loot_container(self,NEAR):
        ''' attempt to loot a container'''
        # NEAR (bool) - keep distance to 500
        distance=2000
        if NEAR:
            distance=500

        item=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_object_container,distance) 

        if item==None:
            return False
        else:
            self.target_object=item
            self.ai_goal='loot_container'
            self.destination=self.target_object.world_coords
            self.ai_state='start_moving'
            self.speak("I'm going to check that "+item.name)
            return True
        

    #-----------------------------------------------------------------------
    def take_action_move_short_random_distance(self):
        distance=random.randint(50,200)
        self.destination=[self.owner.world_coords[0]+float(random.randint(-distance,distance)),self.owner.world_coords[1]+float(random.randint(-distance,distance))]
        self.ai_state='start_moving'
        self.ai_goal='short move'  

    #-----------------------------------------------------------------------
    def take_action_panic(self):
        # adrenaline effect. should allow the bot to run for a bit
        self.fatigue-=50

        self.destination=[self.owner.world_coords[0]+float(random.randint(-2300,2300)),self.owner.world_coords[1]+float(random.randint(-2300,2300))]
        self.ai_state='start_moving'
        self.ai_goal='panic'  
        self.speak('AAaaaaaaahhh!!!!')   

    #-----------------------------------------------------------------------
    def take_action_pickup_object(self,WORLD_OBJECT):
        '''move to and pick up an object'''
        self.target_object=WORLD_OBJECT
        self.ai_goal='pickup'
        self.destination=self.target_object.world_coords
        self.ai_state='start_moving'
        self.speak("I'm going to grab that "+WORLD_OBJECT.name)

    #-----------------------------------------------------------------------
    def think_eat(self):
        '''evaluate food options return bool as to whether something is eaten'''
        status=False

        if self.hunger>75 or self.thirst>50:
            # 1 check if we have anything in inventory
            item=None
            for b in self.inventory:
                if b.is_consumable:
                    item=b
                    break
            if item!=None:
                self.speak('eating '+item.name)
                self.handle_eat(item)
                status=True
            else:
                self.ai_want_food=True

        return status

    #-----------------------------------------------------------------------
    def think_engage(self):
        ''' think about the current engagement'''
        # check if target is still alive
        if self.target_object.ai.health<1:
            self.ai_state='sleeping'
            self.ai_goal='none'
            self.target_object=None
            self.speak('Got him !!')
        else:
            #target is alive, determine the best way to engage
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.target_object.world_coords)
            if distance>300:
                self.think_engage_far(distance)
            else:
                self.think_engage_close(distance)

        # basically if the ai_state doesn't change we will keep firing the next action cycle


    #-----------------------------------------------------------------------
    def think_engage_close(self, DISTANCE):
        ''' engagements <301'''
        # if the ai_state isn't changed the gun will be fired on the next action cycle
        action=False
        if DISTANCE>100:
            # maybe throw a grendate !
            if self.throwable != None:
               self.throw(self.target_object.world_coords)
               action=True
               self.speak('Throwing Grenade !!!!')
        if action==False:
            if self.primary_weapon==None:
                b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns,800)
                if b != None:
                    d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)
                    # make sure its close - we don't want to wander far from the group
                    if d<DISTANCE:
                        action=True
                        self.take_action_pickup_object(b)
            else:
                if self.primary_weapon.ai.get_ammo_count()>1:
                    # we can fire. this will be done automatically
                    action=True
                else:
                    # we are out of ammo
                    # should melee or flee
                    pass 

        if action==False:
            # no way to engage, best to run awaay 
            self.ai_goal='fleeing'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-1300,1300)),self.owner.world_coords[1]+float(random.randint(-1300,1300))]
            self.ai_state='start_moving'
            self.speak('scream')


    #-----------------------------------------------------------------------
    def think_engage_far(self,DISTANCE):
        ''' engagements >301. assumes target is alive'''
        # if no state changes are made the ai will attempt to fire the weapon on the next cycle

        action=False # used locally to help with decision tree
        if self.target_object.is_vehicle:
            if self.antitank!=None:
                self.launch_antitank(self.target_object.world_coords)
                action=True
                self.ai_want_antitank=True

        if action==False:
            if self.primary_weapon==None:
                # take an AT shot
                if self.antitank!=None:
                    self.launch_antitank(self.target_object.world_coords)
                    action=True
                    self.ai_want_gun=True
                    self.ai_want_antitank=True
                else:
                    # engagement is far enough to risk going somewhere to get a gun ??? this needs to be re-thought
                    action=self.take_action_get_gun(False,False)
                    self.speak('Enemies spotted, need to get a gun!')
            # we have a primary weapon
            # check if we are out of ammo
            elif self.primary_weapon.ai.get_ammo_count()<1:
                # we are out of ammo
                self.ai_want_ammo=True
                self.ai_want_gun=True

            else:
                # we have ammo, target is alive

                # check if target is too far 
                if DISTANCE >self.primary_weapon.ai.range :
                    self.ai_goal='close_with_target'
                    self.destination=copy.copy(self.target_object.world_coords)
                    self.ai_state='start_moving'
                    action=True

    #-----------------------------------------------------------------------
    def think_generic(self):
        ''' when the ai_state doesn't have any specific think actions'''
        # what should we be doing ??

        # this is used as a more dynamic alternative to if/else cascades
        action=False

        # 1. are we low on health? 
        if self.health<50 or self.bleeding:
 
            if self.think_healing_options()==False :
                # no health to be had! 
                # roll to see if we panic
                if random.randint(1,25)==1:
                    self.take_action_panic()
                    action=True
            else:
                # bot is applying a bandage or taking a healing action
                action=True

        # health is ok
        if action==False:
            if self.primary_weapon!=None: 
        
                # evaluate personal_enemies
                if len(self.personal_enemies)>0 :

                    # check personal enemy list for a live enemy
                    # if this list is getting big we might make this a one check per turn instead of a loop
                    c=True
                    while c:
                        if len(self.personal_enemies)>0:
                            if self.personal_enemies[0].ai.health<1:
                                self.personal_enemies.pop(0)
                            else:
                                # check distance. pad weapon range a bit as its a rough estimate
                                distance=engine.math_2d.get_distance(self.owner.world_coords,self.personal_enemies[0].world_coords)
                                if distance > (self.primary_weapon.ai.range+20) :
                                    # might as well forget them and check another one
                                    self.personal_enemies.pop(0)
                                else:
                                # engage
                                    self.target_object=self.personal_enemies[0]
                                    self.ai_state='engaging'
                                    self.ai_goal='none'
                                    action=True
                                    c=False # exit while loop
                        else:
                            c=False # exit while loop

                # get a squad enemy  
                if action==False :
                    # get an enemy from the squad
                    self.target_object=self.squad.get_enemy()
                    if self.target_object!=None:
                        self.ai_state='engaging'
                        self.ai_goal='none'
                        action=True
            else:
                # no weapon!
                if len(self.personal_enemies)>0:
                    # no weapon AND we have personal enemies
                    # attempt to get a weapon
                    self.ai_want_gun=True
                    action=self.take_action_get_gun(True,False)

                    if action==False:
                        # we have personal enemies and we don't have a weapon
                        action=True
                        self.take_action_panic()

        
        # got this far with no actions 
        if action==False:

            # important to reset these to false if they are true so 
            # the ai doesn't get stuck here

            if self.ai_want_medical:
                self.ai_want_medical=False
                if self.health<50:
                    self.take_action_get_item(False,self.owner.world.wo_objects_medical)
                else:
                    self.take_action_get_item(True,self.owner.world.wo_objects_medical)
            elif self.ai_want_gun:
                self.ai_want_gun=False
                # maybe this should be (True,False) to get a near gun
                self.take_action_get_gun(False,False)
            elif self.ai_want_ammo:
                self.ai_want_ammo=False
                self.take_action_get_ammo(False)
            elif self.ai_want_cover:
                self.ai_want_cover=False
                # not implemented
            else:
                # note - code may not get here often enough. will have to play test. distance from group is very important
                # distance from group 
                distance_group=engine.math_2d.get_distance(self.owner.world_coords,self.squad.world_coords)
                if distance_group >self.squad.max_distance :
                    self.ai_goal='close_with_group'
                    self.destination=copy.copy(self.squad.world_coords)
                    self.time_since_ai_transition=0
                    self.ai_state='start_moving'
                else:
                    if self.ai_want_food:
                        self.ai_want_food=False
                        self.take_action_get_item(False,self.owner.world.wo_objects_consumable)
                    elif self.ai_want_drink:
                        self.ai_want_drink=False
                        # not implemented
                    elif self.ai_want_grenade:
                        self.ai_want_grenade=False
                        self.take_action_get_item(False,self.owner.world.wo_objects_grenade)
                    elif self.ai_want_antitank:
                        self.ai_want_antitank=False
                        self.take_action_get_item(False,self.owner.world.wo_objects_antitank)
                    else:
                        # want nothing
                        self.think_idle()

    #-----------------------------------------------------------------------
    def think_healing_options(self):
        '''evaluate health options return bool as to whether action is taken'''
        status=False
        # 1 check if we have anything in inventory
        items=[]
        for b in self.inventory:
            if b.is_medical:
                items.append(b)
                #break #why was this here? don't we want all of them?s
        if len(items)>0:
            # pass the whole list and let the function determine the best one to use
            self.handle_use_medical_object(items)
            status=True
        else:
            self.ai_want_medical=True

        # 3 (kind of)
        if self.bleeding:
            if random.randint(1,15)==1:
                self.speak('applying bandage')
                # bleeding stopped through make shift bandage
                self.bleeding=False
                self.health+=5
                self.fatigue+=10
                # i guess this counts as an action
                status=True
        return status

    #-----------------------------------------------------------------------
    def think_idle(self):
        ''' think about very low priority actions to do '''

        # should add some seperate things for civilian and military 
        # no enemies
        # health is fine
        # close to group
        temp=random.randint(0,40)
        action=False
        # upgrade gear
        if temp==0:
            # true if it finds something to upgrade
            action=self.think_upgrade_gear()
        # take a hike 
        elif temp==1:
            self.ai_goal='taking a walk'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-300,300)),self.owner.world_coords[1]+float(random.randint(-300,300))]
            self.ai_state='start_moving'
            action=True
        # much shorter hike
        elif temp==2:
            self.ai_goal='short walk'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
            self.ai_state='start_moving'
            action=True
        # eat something  ?
        elif temp==3:
            action=self.think_eat()
        elif temp==4:
            # loot !!
            action=self.take_action_loot_container(True)
            #print('loot decision '+str(action))


        # catchall if nothing ends up happening 
        if action==False:
            self.ai_goal='waiting'
            self.ai_state='waiting'
            
    #---------------------------------------------------------------------------
    def think_in_vehicle(self):
        ''' in a vehicle - what do we need to do'''

        # the initial decision tree for in vehicle

        # this shouldn't DO much more than change the ai_state
        action=False
        # check vehicle health, should we bail out ?
        if self.vehicle.ai.health<10:
            self.speak('Bailing Out!')
            self.handle_vehicle_died()
            # should probably let everyone else know
            action=True
        # check if we are close to our destination (if we have one)
        elif self.ai_vehicle_goal=='travel':
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.ai_vehicle_destination)
            if distance<50:
                self.handle_exit_vehicle()
                action=True
                # should probably let everyone else know as well
        else:
            print('Error - vehicle goal '+self.ai_vehicle_goal+' is not recognized')


        # basically if we haven't bailed out yet..
        if action==False:

            if self.vehicle.ai.driver==None:
                self.vehicle.ai.driver=self.owner

            if self.vehicle.ai.driver==self.owner:
                self.think_vehicle_drive()
                action=True

            # otherwise if we aren't driving, do we need to do something?

    #-----------------------------------------------------------------------
    def think_loot_container(self,CONTAINER):
        '''look at the contents of a container and take what we need'''
        # written for ai_container but will work for anything that has ai.inventory
        # getting to this function assumes that the bot is <5 from the container
        # and assumes that it exists in teh world

        # assess needs first
        
        medical_items=[]
        consumable_items=[]
        guns=[]
        grenades=[]
        anti_tank=[]
        
        # should handle liquids consumable + fuel

        # should handle ammo containers

        # sort items
        for b in CONTAINER.ai.inventory:
            if b.is_medical:
                medical_items.append(b)
            elif b.is_consumable:
                consumable_items.append(b)
            elif b.is_gun:
                guns.append(b)
            elif b.is_grenade:
                grenades.append(b)
            elif b.is_handheld_antitank:
                anti_tank.append(b)

        # grab stuff based on what we want
        take=[]
        if self.ai_want_medical and len(medical_items)>0:
            take.append(medical_items[0])
            self.ai_want_medical=False
        if self.ai_want_food and len(consumable_items)>0:
            take.append(consumable_items[0])
            self.ai_want_food=False
        if self.ai_want_gun and len(guns)>0:
            take.append(guns[0])
            self.ai_want_gun=False
        if self.ai_want_grenade and len(grenades)>0:
            take.append(grenades[0])
            self.ai_want_grenade=False
        if self.ai_want_antitank and len(anti_tank)>0:
            take.append(anti_tank[0])
            self.ai_want_antitank=False

        if len(take)==0:
            # nothing we wanted. lets grab something random
            chance=random.randint(1,5)
            if chance==1 and len(CONTAINER.ai.inventory)>0:
                take.append(CONTAINER.ai.inventory[0])

        #print('inventory count: '+str(len(CONTAINER.ai.inventory)))
        #print('loot item count: '+str(len(take)))

        # take items!
        for c in take:
            CONTAINER.remove_inventory(c)
            self.event_add_inventory(c)
            self.speak('Grabbed a '+c.name)
            # console log this for now
            #print('bot grabbed '+c.name+' from container '+CONTAINER.name)


    #-----------------------------------------------------------------------
    def think_move(self):
        ''' think about the current movement'''

        # ! note - the logic flow here needs to be re-done. 

        distance=engine.math_2d.get_distance(self.owner.world_coords,self.destination)

        # should we get a vehicle instead of hoofing it to wherever we are going?
        if distance>2000:
            
            # failsafe. we don't want to be going on long trips when we have personal enemies (who are generally close)
            if len(self.personal_enemies)>0:
                self.think_generic()
            else:
                # fine lets go treking across the map
                b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_vehicle,2000)
                if b!=None:

                    # head towards the vehicle
                    # should check if the vehicle is hostile

                    self.ai_vehicle_goal='travel'
                    self.ai_vehicle_destination=copy.copy(self.destination)

                    self.target_object=b
                    self.ai_goal='enter_vehicle'
                    # not using copy here because vehicle may move
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving'
                else:
                    # no vehicles ?
                    pass
        else:
            # another fail safe to stop movement if we are possibly being attacked
            if distance >200 and len(self.personal_enemies)>0:
                self.think_generic()
                print('error ! blocked from movement by close enemy')
            else:
                self.think_move_close(distance)


    #-----------------------------------------------------------------------
    def think_move_close(self,DISTANCE):
        ''' think about movement when you are close to the objective'''
        # close is currently <200
        # we are close to wherever we are going. don't worry about enemies too much

        if self.ai_goal=='pickup':
            if DISTANCE<5:
                if self.target_object in self.owner.world.wo_objects:
                    self.owner.add_inventory(self.target_object)
                    self.owner.world.remove_object(self.target_object)
                else:
                    # hmm object is gone. someone else must have grabbed it
                    pass
                self.ai_state='sleeping'
        if self.ai_goal=='loot_container':
            if DISTANCE<5:
                if self.target_object in self.owner.world.wo_objects:
                    # check contents and grab what we want
                    self.think_loot_container(self.target_object)
                else:
                    # hmm object is gone. someone else must have grabbed it
                    # this is especially odd because it is a container
                    print('error: container is unexpectedly missing')
                    pass
                self.ai_state='sleeping'
        elif self.ai_goal=='enter_vehicle':

            # vehicles move around a lot so gotta check
            if self.destination!=self.target_object.world_coords:
                self.destination=copy.copy(self.target_object.world_coords)
                self.ai_state='start_moving'
            else:
                if DISTANCE<5:
                    if self.target_object in self.owner.world.wo_objects:
                        self.handle_enter_vehicle(self.target_object)

                    else:
                        # hmm object is gone. idk how that happened
                        print('object I was going to enter disappeared')
                        pass
                    self.ai_state='sleeping'
        elif self.ai_goal=='get_ammo':
            if DISTANCE<5:
                print('replenishing ammo ')
                # get max count of fully loaded magazines
                self.primary_weapon.ai.magazine_count=self.primary_weapon.ai.max_magazines
                self.ai_state='sleeping'
        elif self.ai_goal=='close_with_target':
            if self.target_object==None:
                print('warn: ai_goal is close_with_target but target is None')
                self.ai_goal='none'
            else:
                # check if target is dead 
                if self.target_object.ai.health<1:
                    self.ai_state='sleeping'
                    self.ai_goal='none'
                    self.target_object=None
                elif DISTANCE<self.primary_weapon.ai.range:
                    self.ai_state='engaging'
                    self.ai_goal='none'
                else:
                    # failsafe to keep us from chasing enemies when closer ones are nearby
                    # personal enemies are generally close by
                    if len(self.personal_enemies)>0:
                        self.think_generic()
                    else:
                        # reset the destination coordinates
                        self.ai_goal='close_with_target'
                        self.destination=copy.copy(self.target_object.world_coords)
                        self.ai_state='start_moving'
        elif self.ai_goal=='close_with_group':
            if DISTANCE<self.squad.min_distance:
                self.ai_state='sleeping'
        elif self.ai_goal=='player_move':
            # this is initiated from world.select_with_mouse when
            # the selected object is too far away
            if DISTANCE<35:
                self.ai_state='sleeping'
                self.ai_goal='none'
                # basically disables the bot again. wait for player
                # interaction or another timeout
                self.time_since_player_interact=0
        else:
            #print('error: unhandled moving goal: '+self.ai_goal)
            # catchall for random moving related goals:
            if DISTANCE<5:
                self.ai_state='sleeping'

    #-----------------------------------------------------------------------
    def think_upgrade_gear(self):
        '''think about upgrading gear. return True/False if upgrading'''

        # !! this is kinda pointless as most of this stuff is also done under think_generic now
        # maybe make it more thinky than think_generic which is kind of a last ditch find something to do 
        # method 

        status=False
        # grab another grenade?
        if self.throwable == None:
            status=self.take_action_get_item(True,self.owner.world.wo_objects_grenade)
        # upgrade weapon?
        if status==False:
            # will attempt to upgrade gun, or get any nearby gun if ai doesn't have one
            status=self.take_action_get_gun(True,True)
        # grab anti-tank 
        if status==False and self.antitank==None:
            status=self.take_action_get_item(True,self.owner.world.wo_objects_handheld_antitank)

        # upgrade clothes / armor

        # top off ammo ?
        if status==False and self.primary_weapon!=None:
            if self.primary_weapon.ai.get_ammo_count()<(self.primary_weapon.ai.get_max_ammo_count()*.5):
                # ammo half out or less
                # top off near ammo if possible
                status=self.take_action_get_ammo(True)


        return status

    #---------------------------------------------------------------------------
    def think_vehicle_drive(self):
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        # get the rotation to the destination 
        r = engine.math_2d.get_rotation(self.owner.world_coords,self.ai_vehicle_destination)

        # compare that with the current vehicle rotation.. somehow?
        v = self.vehicle.rotation_angle

        if r>v:
            #self.vehicle.rotation_angle+=1*time_passed
            #self.vehicle.reset_image=True
            self.vehicle.ai.handle_steer_left()
        if r<v:
            #self.vehicle.rotation_angle-=1*time_passed
            #self.vehicle.reset_image=True
            self.vehicle.ai.handle_steer_right()
        
        # if its close just set it equal
        if r>v-5 and r<v+5:
            self.vehicle.rotation_angle=r
            self.vehicle.reset_image=True


        self.vehicle.ai.throttle=1
        self.vehicle.ai.brake_power=0

    #---------------------------------------------------------------------------
    def throw(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man '''    
        if self.throwable!=None:
            self.throwable.ai.throw(TARGET_COORDS)
            self.owner.world.add_object(self.throwable)
            self.inventory.remove(self.throwable)
            self.throwable=None
