
'''
module : ai_player.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
event - something that could happen to the ai, possibly caused by external forces
handle_SOMETHING - something that the AI decides to do
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
    def fire(self,TARGET_COORDS):
        ''' fires the (primary?) weapon '''    
        if self.primary_weapon!=None:
            self.primary_weapon.ai.fire(self.owner.world_coords,TARGET_COORDS)


    #---------------------------------------------------------------------------
    def get_calculated_speed(self):
        calc_speed=self.owner.speed
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
    def handle_death(self):
        dm=''
        dm+=(self.owner.name+' died.')
        dm+=('\n  - faction: '+self.squad.faction)
        dm+=('\n  - confirmed kills: '+str(self.confirmed_kills))
        dm+=('\n  - killed by : '+self.last_collision_description)
        print(dm)

        # drop inventory 
        for b in self.inventory:
            b.world_coords=[self.owner.world_coords[0]+float(random.randint(-15,15)),self.owner.world_coords[1]+float(random.randint(-15,15))]
            self.owner.world.add_object(b)

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

        self.owner.world.remove_object(self.owner)

        if self.owner.is_player:
            # turn on the player death menu
            self.owner.world.world_menu.active_menu='death'
            self.owner.world.world_menu.menu_state='none'
            # fake input to get the text added
            self.owner.world.world_menu.handle_input('none')


    #---------------------------------------------------------------------------
    def handle_eat(self,CONSUMABLE):
        # eat the consumable object. or part of it anyway
        self.health+=CONSUMABLE.ai.health_effect
        self.hunger+=CONSUMABLE.ai.hunger_effect
        self.thirst_rate+=CONSUMABLE.ai.thirst_effect
        self.fatigue+=CONSUMABLE.ai.fatigue_effect

        self.event_remove_inventory(CONSUMABLE)

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

        if self.ai_state=='moving':
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
                    self.destination=[self.owner.world_coords[0]+float(random.randint(-2300,2300)),self.owner.world_coords[1]+float(random.randint(-2300,2300))]
                    self.ai_state='start_moving'
                    self.ai_goal='panic'
                    self.speak('scream')

                    
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
                self.fire(self.target_object.world_coords)
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
            else:
                # sleeping or whatever 
                self.fatigue-=self.fatigue_remove_rate*time_passed


    #---------------------------------------------------------------------------
    def handle_player_update(self):
        ''' handle any player specific code'''
        action=False
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        if(self.owner.world.graphic_engine.keyPressed('w')):
            self.owner.world_coords[1]-=self.owner.speed*time_passed
            self.owner.rotation_angle=0
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('s')):
            self.owner.world_coords[1]+=self.owner.speed*time_passed
            self.owner.rotation_angle=180
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('a')):
            self.owner.world_coords[0]-=self.owner.speed*time_passed
            self.owner.rotation_angle=90
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('d')):
            self.owner.world_coords[0]+=self.owner.speed*time_passed
            self.owner.rotation_angle=270
            self.owner.reset_image=True
            action=True
        if(self.owner.world.graphic_engine.keyPressed('f')):
            # fire the gun
            self.fire(self.owner.world.graphic_engine.get_mouse_world_coords())
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
        else:
            if self.fatigue>0:
                self.fatigue-=self.fatigue_remove_rate*time_passed

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
        ''' say something the ai is close to the player '''
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
    def think_eat(self):
        '''evaluate food options return bool as to whether action is taken'''
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

            # 2 else check if anything is nearby
            if status==False:
                o=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_consumable,500)
                if o != None:
                    self.target_object=o
                    self.ai_goal='pickup'
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving'
                    status=True
        return status

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
                self.think_engage_far(distance)
            else:
                self.think_engage_close(distance)

        # basically if the ai_state doesn't change we will keep firing the next action cycle

    def think_engage_close(self, DISTANCE):
        ''' engagements <301'''
        # if the ai_state isn't changed the gun will be fired on the next action cycle
        action=False
        if DISTANCE>100:
            # maybe throw a grendate !
            if self.throwable != None:
               self.throw(self.target_object.world_coords)
               action=True
        if action==False:
            if self.primary_weapon==None:
                b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns,800)
                if b != None:
                    d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)
                    # make sure its close - we don't want to wander far from the group
                    if d<DISTANCE:
                        action=True
                        self.target_object=b
                        self.ai_goal='pickup'
                        self.destination=self.target_object.world_coords
                        self.ai_state='start_moving'
            else:
                if self.primary_weapon.ai.magazine>0:
                    # we can fire. this will be done automatically
                    action=True 

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

        if action==False:
            if self.primary_weapon==None:
                # engagement is far enough to risk going somewhere to get a gun ??? this needs to be re-thought
                self.target_object=self.owner.world.get_closest_gun(self.owner.world_coords)
                self.ai_goal='pickup'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving'
                action=True
            # we have a primary weapon
            # check if we are out of ammo
            elif self.primary_weapon.ai.get_ammo_count()<1:
                # we are out of ammo
                # get more ammo 
                self.target_object=self.owner.world.get_closest_ammo_source(self.owner)
                self.ai_goal='get ammo'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving'
                action=True
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
                # no health to be had! (probably impossible with the amount of consumables)
                # roll to see if we panic
                if random.randint(1,25)==1:
                    self.destination=[self.owner.world_coords[0]+float(random.randint(-2300,2300)),self.owner.world_coords[1]+float(random.randint(-2300,2300))]
                    self.ai_state='start_moving'
                    self.ai_goal='panic'
                    print('bot panicking from think_generic')
                    action=True 
            else:
                # bot is doing whatever the healing option was
                # this is needed in case the health option is to go pickup health
                action=True

        # possibly engage a enemy
        if action==False and self.primary_weapon!=None: 
        
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

        
        # got this far with no actions 
        if action==False:
            # distance from group 
            distance_group=engine.math_2d.get_distance(self.owner.world_coords,self.squad.world_coords)
            if distance_group >self.squad.max_distance :
                self.ai_goal='close_with_group'
                self.destination=copy.copy(self.squad.world_coords)
                self.time_since_ai_transition=0
                self.ai_state='start_moving'
            else:
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
                break
        if len(items)>0:
            # pass the whole list and let the function determine the best one to use
            self.handle_use_medical_object(items)
            status=True

        # 2 else check if anything is nearby
        if status==False:
            o=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_medical,800)
            if o != None:
                self.target_object=o
                self.ai_goal='pickup'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving'
                status=True

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
        ''' think about low priority actions to do '''
        # no enemies
        # health is fine
        # close to group
        temp=random.randint(0,10)
        action=False
        # upgrade gear
        if temp==0:
            # true if it finds something to upgrade
            action=self.think_upgrade_gear()
        # take a hike 
        elif temp==1:
            self.ai_goal='booored'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-300,300)),self.owner.world_coords[1]+float(random.randint(-300,300))]
            self.ai_state='start_moving'
            action=True
        # much shorter hike
        elif temp==2:
            self.ai_goal='booored'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-30,30)),self.owner.world_coords[1]+float(random.randint(-30,30))]
            self.ai_state='start_moving'
            action=True
        # eat something  ?
        elif temp==3:
            action=self.think_eat()

        # catchall if nothing ends up happening 
        if action==False:
            self.ai_goal='waiting'
            self.ai_state='waiting'
            


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
                    self.ai_goal='enter object'
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
        elif self.ai_goal=='enter object':

            # vehicles move around a lot so gotta check
            if self.destination!=self.target_object.world_coords:
                self.destination=copy.copy(self.target_object.world_coords)
                self.ai_state='start_moving'
            else:
                if DISTANCE<5:
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
            if DISTANCE<5:
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
        else:
            # catchall for random moving related goals:
            if DISTANCE<3:
                self.ai_state='sleeping'
    #-----------------------------------------------------------------------
    def think_upgrade_gear(self):
        '''think about upgrading gear. return True/False if upgrading'''
        status=False
        # grab another grenade?
        if self.throwable == None:
            b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_grenade,500)
            if b != None:
                status=True
                self.target_object=b
                self.ai_goal='pickup'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving' 

        # upgrade weapon?
        if status==False:
            if self.primary_weapon!=None:
                if self.primary_weapon.ai.type=='pistol' or self.primary_weapon.ai.type=='rifle':
                    b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns,500)
                    if b != None:
                        # the thought here being that riles are undesirable, and a mg is crew served and unlikely to 
                        # be picked up
                        if b.ai.type=='submachine gun' or b.ai.type=='assault rifle':
                            status=True
                            self.target_object=b
                            self.ai_goal='pickup'
                            self.destination=self.target_object.world_coords
                            self.ai_state='start_moving' 

            else:
                # pickup any gun that is close
                b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns,500)
                if b != None:
                    status=True
                    self.target_object=b
                    self.ai_goal='pickup'
                    self.destination=self.target_object.world_coords
                    self.ai_state='start_moving' 

        # grab anti-tank 
        if status==False and self.antitank==None:
            b=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_handheld_antitank,500)
            if b != None:
                status=True
                self.target_object=b
                self.ai_goal='pickup'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving' 

        # upgrade clothes / armor

        # top off ammo ?

        return status
    #---------------------------------------------------------------------------
    def throw(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man '''    
        if self.throwable!=None:
            self.throwable.ai.throw(TARGET_COORDS)
            self.owner.world.add_object(self.throwable)
            self.inventory.remove(self.throwable)
            self.throwable=None
