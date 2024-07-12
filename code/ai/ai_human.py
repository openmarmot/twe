
'''
module : ai_player.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
event - something that could happen to the ai, possibly caused by external forces
handle_SOMETHING - something that the AI decides to do that requires some code to make happen
take_action_ - something simple that sets ai_state and ai_goal to start an action, but not a lot of logic
think_ - something that requires a lot of logic code
react_ - player or bot calls this when they want to give orders to another bot
for humans the current owner.image_list is [normal,prone,dead]
'''

#import built in modules
import random
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder


#global variables

class AIHuman(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # equipment
        self.primary_weapon=None
        self.throwable=None
        self.antitank=None
        self.melee=None

        self.wearable_head=None
        self.wearable_upper_body=None
        self.wearable_lower_body=None
        self.wearable_feet=None
        self.wearable_hand=None

        # skills
        self.is_pilot=False



        # objects that are large_human_pickup. only one at a time
        self.large_pickup=None

        # vector offset for when you are carrying a object
        self.carrying_offset=[10,10]

        self.health=100
        self.bleeding=False
        self.time_since_bleed=0
        self.bleed_interval=0.5

        self.prone=False

        self.confirmed_kills=0
        self.probable_kills=0

        # a description of whatever collided with this object last. 
        self.last_collision_description=''

        # what the ai is actually doing (an action)
        self.ai_state='none'
        # - waiting : if a vehicle driver will cause the driver to wait with the brake on for the wait_interval

        # what the ai is trying to accomplish
        self.ai_goal='none'

        # ai 'waiting' state timer 
        self.time_since_asked_to_wait=0
        self.wait_interval=60

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
        # the job that the ai is performing in the vehicle
        self.ai_vehicle_role=None # driver / gunner / passenger 
        # the turret the human is controlling if they are a gunner
        self.vehicle_turret=None


        self.in_building=False
        self.building_list=[] # list of buildings the ai is overlapping spatially
        self.time_since_building_check=0
        self.building_check_rate=1

        self.time_since_ai_transition=0.
        self.ai_think_rate=0
        # the ai group that this human is a part of 
        self.squad=None
        self.squad_min_distance=30
        self.squad_max_distance=300
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

        # target lists. these are refreshed periodically 
        self.near_targets=[]
        self.mid_targets=[]
        self.far_targets=[]
        self.time_since_target_evaluation=0
        self.target_eval_rate=random.uniform(0.1,0.9)

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

        # max distance that is walkable before deciding a vehicle is better 
        self.max_walk_distance=2000

    #---------------------------------------------------------------------------
    def calculate_projectile_damage(self,projectile):
        '''calculate and apply damage from projectile hit'''

        bleeding_hit=False
        hit=random.randint(1,5)
        if hit==1:
            #head
            self.health-=random.randint(85,100)
            bleeding_hit=True
                
        elif hit==2:
            #upper body
            self.health-=random.randint(50,80)
            bleeding_hit=True
        elif hit==3:
            #lower body
            self.health-=random.randint(30,60)
            bleeding_hit=True
        elif hit==4:
            # feet
            self.health-=random.randint(30,40)
            bleeding_hit=True
        elif hit==5:
            # hands
            self.health-=random.randint(30,40)
            bleeding_hit=True
        
        if bleeding_hit:
            self.bleeding=True
            engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'blood_splatter',True)
            if self.owner.is_player:
                self.owner.world.graphic_engine.text_queue.insert(0,'You are hit and begin to bleed')

        self.speak('react to being shot')

        

    #---------------------------------------------------------------------------
    def evaluate_targets(self):
        '''find and categorzie targets'''
        target_list=[]
        if self.squad.faction=='german':
            target_list=self.owner.world.wo_objects_soviet+self.owner.world.wo_objects_american
        elif self.squad.faction=='american':
            target_list=self.owner.world.wo_objects_soviet+self.owner.world.wo_objects_german
        elif self.squad.faction=='soviet':
            target_list=self.owner.world.wo_objects_german+self.owner.world.wo_objects_american
        elif self.squad.faction=='civilian':
            pass
        else:
            print('error! unknown squad faction!')

        self.near_targets=[]
        self.mid_targets=[]
        self.far_targets=[]

        for b in target_list:
            d=engine.math_2d.get_distance(self.owner.world_coords,b.world_coords)

            if d<500:
                self.near_targets.append(b)
            elif d<850:
                self.mid_targets.append(b)
            elif d<1300:
                self.far_targets.append(b)

    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        self.last_collision_description=''
        if event_data.is_projectile:
            distance=engine.math_2d.get_distance(self.owner.world_coords,event_data.ai.starting_coords,True)
            self.last_collision_description='hit by '+event_data.name + ' at a distance of '+ str(distance)
            starting_health=self.health

            self.calculate_projectile_damage(event_data)

            # add the shooter of the bullet to the personal enemies list
            # shrapnel from grenades and panzerfausts dont track ownership
            if event_data.ai.shooter !=None:
                self.last_collision_description+=(' from '+event_data.ai.shooter.name)

                if event_data.ai.shooter.ai.squad != None:
                    if event_data.ai.shooter.ai.squad.faction != self.squad.faction or event_data.ai.shooter.is_player:
                        # this creates a lot of friendly fire - but its interesting 
                        self.personal_enemies.append(event_data.ai.shooter)

                # kill tracking
                # just focus on humans for now
                if event_data.ai.shooter.is_human:
                    if self.health<30:
                        # protects from recording hits on something that was already dead
                        if starting_health>0:
                            if self.health<1:
                                event_data.ai.shooter.ai.confirmed_kills+=1
                            else:
                                event_data.ai.shooter.ai.probable_kills+=1
                        else:
                            print('collision on a dead human ai detected')

                    if event_data.ai.shooter.ai.primary_weapon!=None:
                        self.last_collision_description+=("'s "+event_data.ai.weapon_name)
            else:
                if event_data.ai.shooter==None:
                    print('Error - projectile shooter is none')
                # other way to get here is if its not a projectile
                print('or its not a projectile')

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

        elif event_data.is_grenade:
            # not sure what to do here. the grenade explodes too fast to really do anything

            # attempt to throw the grenade back
            if random.randint(1,5)==1:
                event_data.ai.redirect(event_data.ai.equipper.world_coords)
            else:
                self.ai_goal='react to collision'
                self.destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
                self.ai_state='start_moving'
        elif event_data.is_throwable:
            #throwable but not a grenade 
            self.speak('Oww!')
            # temp do something else later
            self.take_action_panic()

        else:
            print('unidentified collision')

            # this is very important because it breaks us out of whatever ai cycle we were in
            # we are put in a very short movement cycle and then the AI can 'think' about what to do next
            self.ai_goal='react to collision'
            self.destination=[self.owner.world_coords[0]+float(random.randint(-60,60)),self.owner.world_coords[1]+float(random.randint(-60,60))]
            self.ai_state='start_moving'

    #---------------------------------------------------------------------------
    def event_add_inventory(self,event_data):
        ''' add object to inventory. does not remove obj from world'''
        if event_data not in self.inventory:
            if event_data.is_large_human_pickup:
                # note - this will happen when a large_human_pickup is in another container
                # for example if a fuel can is in a kubelwagen
                # this does NOT happen when an object is picked up from the world as it is intercepted
                # before it gets this far

                #add to world. (the object was in a inventory array)
                self.owner.world.add_queue.append(event_data)

                self.large_pickup=event_data

            else:

                self.inventory.append(event_data)

                if event_data.is_gun :
                    if self.primary_weapon!=None:
                        # drop the current obj and pick up the new one
                        self.handle_drop_object(self.primary_weapon)
                    if self.owner.is_player :
                        self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.primary_weapon=event_data
                    event_data.ai.equipper=self.owner
                    self.ai_want_gun=False
                elif event_data.is_throwable :
                    if self.throwable==None:
                        if self.owner.is_player :
                            self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                        self.throwable=event_data
                        event_data.ai.equipper=self.owner
                    if event_data.is_grenade:
                        self.ai_want_grenade=False
                elif event_data.is_handheld_antitank :
                    if self.antitank!=None:
                        # drop the current obj and pick up the new one
                        self.handle_drop_object(self.antitank)
                    if self.owner.is_player :
                        self.owner.world.graphic_engine.text_queue.insert(0,'[ '+event_data.name + ' equipped ]')
                    self.antitank=event_data
                    event_data.ai.equipper=self.owner
                    self.ai_want_antitank=False
                elif event_data.is_consumable:
                    self.ai_want_food=False
                elif event_data.is_medical:
                    self.ai_want_medical=False
                elif event_data.is_wearable:
                    if event_data.ai.wearable_region=='head':
                        if self.wearable_head==None:
                            self.wearable_head=event_data
        else:
            print('ERROR - object '+event_data.name+' is already in inventory')
            print('inventory list:')
            for b in self.inventory:
                print(' - ',b.name)


    #---------------------------------------------------------------------------
    def event_remove_inventory(self,event_data):
        ''' remove object from inventory. does NOT add to world '''

        if event_data in self.inventory:

            self.inventory.remove(event_data)
            # NOTE - if this object is meant to be added to the world it should be done by whatever calls this

            if self.primary_weapon==event_data:
                self.primary_weapon=None
                event_data.ai.equipper=None
            elif self.throwable==event_data:
                self.throwable=None
                # equipper is used to figure out who threw the grenade
                # need a better way to handle this in the future
                #EVENT_DATA.ai.equipper=None
            elif self.antitank==event_data:
                self.antitank=None
                event_data.ai.equipper=None
            elif self.large_pickup==event_data:
                print('ERROR - large pickup should not go through inventory functions')
            elif self.wearable_head==event_data:
                self.wearable_head=None

            # need to add a method call here that will search inventory and add new weapon/grendade/whatever if available

        else:
            print('removal error - object not in inventory',event_data.name)

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
        if self.prone:
            calc_speed*=0.5
        
        return calc_speed
    
    #---------------------------------------------------------------------------
    def get_target(self):
        '''returns a target or None if there are None'''
        target=None
        if len(self.near_targets)>0:
            target=self.near_targets.pop()
        elif len(self.mid_targets)>0:
            target=self.mid_targets.pop()
        elif len(self.far_targets)>0:
            target=self.far_targets.pop()

        if target!=None:
            if target.ai.health<1:
                # could get intesting if there are a lot of dead targets but 
                # it should self clear with this recursion
                print('error: got dead target: '+target.name+' retrying')
                print('near ',len(self.near_targets))
                print('mid',len(self.mid_targets))
                print('far',len(self.far_targets))
                target=self.get_target()
                

        return target
    
    #---------------------------------------------------------------------------
    def handle_aim_and_fire_weapon(self,weapon):
        ''' handles special aiming and firing code for various targets'''
        aim_coords=self.target_object.world_coords
        # guess how long it will take for the bullet to arrive
        time_passed=random.uniform(0.8,1.5)
        if self.target_object.is_vehicle:
            vehicle=self.target_object.ai.vehicle
            if self.target_object.ai.vehicle.ai.current_speed>0:
                aim_coords=engine.math_2d.moveAlongVector(vehicle.ai.current_speed,vehicle.world_coords,vehicle.heading,time_passed)

        if self.target_object.is_human:
            if self.target_object.ai.in_vehicle:
                vehicle=self.target_object.ai.vehicle
                if self.target_object.ai.vehicle.ai.current_speed>0:
                    aim_coords=engine.math_2d.moveAlongVector(vehicle.ai.current_speed,vehicle.world_coords,vehicle.heading,time_passed)
            
            else:
                if self.target_object.ai.ai_state=='moving':    
                    aim_coords=engine.math_2d.moveTowardsTarget(self.target_object.ai.get_calculated_speed(),aim_coords,self.target_object.ai.destination,time_passed)


        self.fire(aim_coords,weapon)

    #---------------------------------------------------------------------------
    def handle_building_check(self):

        # reset transition to zero
        self.time_since_building_check=0

        # randomize time before we hit this method again
        self.building_check_rate=random.uniform(0.1,1.5)
        # clear building list and in_building bool
        self.building_list=[]
        self.in_building=False
        # check to see if we are colliding with any of the buildings
        for b in self.owner.world.wo_objects_building:
            if engine.math_2d.checkCollisionCircleOneResult(self.owner,[b],[]) !=None:
                self.building_list.append(b)
                self.in_building=True

    #---------------------------------------------------------------------------
    def handle_change_vehicle_role(self,ROLE):
        ''' change your role on the vehicle crew'''
        # ROLE : driver , gunner, passenger, none
        if self.in_vehicle:

            # remove from existing roles
            self.ai_vehicle_role='none'
            for b in self.vehicle.ai.turrets:
                if b.ai.gunner==self.owner:
                    b.ai.gunner=None
                    self.vehicle_turret=None

            if self.vehicle.ai.driver==self.owner:
                self.vehicle.ai.driver=None
                # turn on the brakes to prevent roll away
                self.vehicle.ai.brake_power=1

            if ROLE=='driver':
                if self.vehicle.ai.driver!=self.owner.world.player:
                    if self.vehicle.ai.driver!=None:
                        self.vehicle.ai.driver.ai.ai_vehicle_role='none'
                    self.vehicle.ai.driver=self.owner
                    self.ai_vehicle_role='driver'
                    self.speak("Taking over driving")

                    # check if anyone is trying to get in the vehicle
                    new_passengers=0
                    for c in self.owner.world.wo_objects_human:
                        if c.ai.ai_goal=='enter_vehicle' and c.ai.target_object==self.vehicle:
                            new_passengers+=1
                    if new_passengers>0:
                        # politely remind yourself to wait a minute so they can get in
                        self.react_asked_to_wait()
                    
            elif ROLE=='gunner':
                for b in self.vehicle.ai.turrets:
                    if b.ai.gunner==None:
                        self.speak("Taking over gunner position")
                        b.ai.gunner=self.owner
                        self.vehicle_turret=b
                        self.ai_vehicle_role='gunner'
                        break

            elif ROLE=='passenger':
                # nothing to do here, roles already removed
                pass
            else :
                # 'none' is used to remove all roles
                if ROLE!='none':
                    print('error: handle_change_vehicle_role - role not recognized ',ROLE)

        else: 
            print('error: attempting to change vehicle role when not in vehicle')

    #---------------------------------------------------------------------------
    def handle_check_ammo(self,gun):
        '''check ammo and magazines for a gun'''
        # gun - a world object with ai_gun
        # check_inventory - bool. if true also check inventory
        # return [ammo in gun, ammo in inventory]
        ammo_gun=0
        if gun.ai.magazine!=None:
            ammo_gun=len(gun.ai.magazine.ai.projectiles)

        ammo_inventory=0
        magazine_count=0
        for b in self.inventory:
            if b.is_gun_magazine:
                if gun.name in b.ai.compatible_guns:
                    ammo_inventory+=len(b.ai.projectiles)
                    magazine_count+=1


        return [ammo_gun,ammo_inventory,magazine_count]        

    #---------------------------------------------------------------------------
    def handle_check_near_magazines(self,weapon,range=50):
        ''' check nearby surroundings for specific magazines'''

        # can something more useful be done here ? 

        # for now we will return a list of nearby magazines, in the future maybe 
        # actually do something like create tasks 

        near_mags=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_gun_magazines,range)
        correct_mags=[]
        for b in near_mags:
            if weapon.name in b.ai.compatible_guns:
                correct_mags.append(b)

        return near_mags

    #---------------------------------------------------------------------------
    def handle_death(self):
        dm=''
        dm+=(self.owner.name+' died.')
        dm+=('\n  - faction: '+self.squad.faction)
        dm+=('\n  - confirmed kills: '+str(self.confirmed_kills))
        dm+=('\n  - probable kills: '+str(self.probable_kills))
        dm+=('\n  - killed by : '+self.last_collision_description)
        
        # exit vehicle 
        if self.in_vehicle:
            self.handle_exit_vehicle()

        # drop primary weapon 
        if self.primary_weapon!=None:
            ammo=self.handle_check_ammo(self.primary_weapon)
            dm+=('\n  - weapon: '+self.primary_weapon.name)
            dm+=('\n  -- ammo in gun: '+str(ammo[0]))
            dm+=('\n  -- ammo in inventory: '+str(ammo[1]))
            dm+=('\n  -- magazine count: '+str(ammo[2]))

            self.handle_drop_object(self.primary_weapon)

        if self.large_pickup!=None:
            self.handle_drop_object(self.large_pickup)

        # remove from squad 
        if self.squad != None:
            if self.owner in self.squad.members:
                self.squad.members.remove(self.owner)

                if self.owner==self.squad.squad_leader:
                    self.squad.squad_leader=None
            else: 
                # note this just in case but the bug causing this was fixed.
                print('!! Error : '+self.owner.name+' not in squad somehow')

        # spawn body
        engine.world_builder.spawn_container('body: '+self.owner.name,self.owner.world,self.owner.world_coords,self.owner.rotation_angle,self.owner.image_list[2],self.inventory)

        # remove from world
        self.owner.world.remove_queue.append(self.owner)

        if self.owner.is_player:
            # turn on the player death menu
            self.owner.world.world_menu.active_menu='death'
            self.owner.world.world_menu.menu_state='none'
            # fake input to get the text added
            self.owner.world.world_menu.handle_input('none')
    
        #print death message
        print(dm)

    #---------------------------------------------------------------------------
    def handle_drink(self,LIQUID):
        print('drinking no longer implemented')

    #---------------------------------------------------------------------------
    def handle_drop_object(self,OBJECT_TO_DROP):
        ''' drop object into the world '''
        # any distance calculation would be made before this function is called
        if OBJECT_TO_DROP.is_large_human_pickup:
            self.large_pickup=None
        else:
            self.event_remove_inventory(OBJECT_TO_DROP)
            # make sure the obj world_coords reflect the obj that had it in inventory
            OBJECT_TO_DROP.world_coords=copy.copy(self.owner.world_coords)
            
            # grenades get 'dropped' when they are thrown and are special
            if OBJECT_TO_DROP.is_grenade==False:
                engine.math_2d.randomize_position_and_rotation(OBJECT_TO_DROP)
            self.owner.world.add_queue.append(OBJECT_TO_DROP)

    #---------------------------------------------------------------------------
    def handle_eat(self,CONSUMABLE):
        # eat the consumable object. or part of it anyway
        self.health+=CONSUMABLE.ai.health_effect
        self.hunger+=CONSUMABLE.ai.hunger_effect
        self.thirst+=CONSUMABLE.ai.thirst_effect
        self.fatigue+=CONSUMABLE.ai.fatigue_effect

        # this should remove the object from the game because it is not added to world
        self.event_remove_inventory(CONSUMABLE)

    #---------------------------------------------------------------------------
    def handle_enter_vehicle(self,VEHICLE):
        # should maybe pick driver or gunner role here
       
        # reset ai
        self.reset_ai()

        # check the vehicle still exists
        if self.owner.world.check_object_exists(VEHICLE)==False:
            self.speak('Where did that '+VEHICLE.name+' go?')
        else:
            precheck=True
            if VEHICLE.ai.max_occupants<=len(VEHICLE.ai.passengers):
                precheck=False
                self.speak('No more room in this vehicle!')
            
            if VEHICLE.ai.driver!=None:
                if VEHICLE.ai.driver.ai.squad.faction!=self.squad.faction:
                    precheck=False
                    self.speak('The enemy took this vehicle!')
            
            if precheck:
                # put your large items in the trunk
                if self.large_pickup:
                    VEHICLE.add_inventory(self.large_pickup)
                    self.owner.world.remove_queue.append(self.large_pickup)
                    self.large_pickup=None

                VEHICLE.ai.passengers.append(self.owner)
                self.in_vehicle=True
                self.vehicle=VEHICLE
                self.ai_goal='in_vehicle'
                self.ai_state='in_vehicle'
                
                if self.vehicle.ai.open_top==False:
                    # human is hidden by top of vehicle so don't render
                    self.owner.render=False

                if self.vehicle.ai.driver==None:
                    self.handle_change_vehicle_role('driver')


    #---------------------------------------------------------------------------
    def handle_exit_vehicle(self):
        if self.in_vehicle:
            # remove self from any vehicle roles
            self.handle_change_vehicle_role('none')
            self.in_vehicle=False
            self.vehicle.ai.passengers.remove(self.owner)
            self.vehicle=None
            self.reset_ai()
            self.ai_vehicle_destination=None # reset this so things don't get funky

            # make sure we are visible again
            self.owner.render=True

            # move a tiny bit so everyone isn't in the exact same spot
            self.owner.world_coords=[self.owner.world_coords[0]+float(random.randint(-7,7)),self.owner.world_coords[1]+float(random.randint(-7,7))]

            # maybe grab your large pick up if you put it in the trunk
            
            self.speak('Jumping out')
        else:
            print('error: handle_exit_vehicle called but not in vehicle')

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
    def handle_keydown(self,key):
        ''' handle keydown passed from world.handle_keydown'''
        # this is a one off key press, not press and hold
        # world.handle_keydown will pass the key as the actual keyboard letter

        if self.in_vehicle:
            if self.vehicle.is_airplane:
                if key=='p':
                    self.handle_exit_vehicle()
                    self.speak('bailing out!')
                    # note - physics needs to be udpdate to handle falling
        else:
            # controls for when you are walking about

            if key=='b':
                print('note - bandaging is now done through the player medical menu ')
                pass
            elif key=='g':
                self.throw([])
            elif key=='p':
                self.handle_prone_state_change()
            elif key=='r':
                self.handle_player_reload()
            elif key=='t':
                self.launch_antitank([])

    #-----------------------------------------------------------------------
    def handle_normal_ai_think(self):
        ''' normal AI thinking method '''
        # this is basically a thinking state - check the current progress on whatever 
        # the ai thinks it is doing

        # reset transition to zero
        self.time_since_ai_transition=0

        # randomize time before we hit this method again
        self.ai_think_rate=random.uniform(0.1,1.5)

        if self.ai_state=='waiting':
            if self.time_since_asked_to_wait>self.wait_interval:
                self.ai_state='none'
                self.ai_goal='none'


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
            if self.in_vehicle:
                # maybe need more nuance to this. is there a good reason to be in a vehicle if you are almost dead?
                self.handle_exit_vehicle()
                print('debug: human exited vehicle because human health<10')

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

        # identify and categorize targets
        self.time_since_target_evaluation+=time_passed
        if self.time_since_target_evaluation>self.target_eval_rate :
            self.target_eval_rate=random.uniform(0.8,6.5)
            self.evaluate_targets()

        self.time_since_asked_to_wait+=time_passed

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
                    self.handle_aim_and_fire_weapon(self.primary_weapon)
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
        
        # graphic_engine.keyPressed works for keys that need to be held down
        # keys that should trigger an event only when they keydown (once) are handled 
        # by world.handle_keydown()

        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        if self.in_vehicle:

            if self.ai_vehicle_role=='driver':

                if self.vehicle.is_airplane:
                    # ---- controls for airplanes ------------
                    if(self.owner.world.graphic_engine.keyPressed('w')):
                        self.vehicle.ai.handle_elevator_up()
                    if(self.owner.world.graphic_engine.keyPressed('s')):
                        self.vehicle.ai.handle_elevator_down()
                        if self.owner.altitude<1:
                            self.vehicle.ai.brake_power=1
                    if(self.owner.world.graphic_engine.keyPressed('a')):
                        self.vehicle.ai.handle_aileron_left()
                        self.vehicle.ai.handle_rudder_left()
                        if self.owner.altitude<1:
                            self.vehicle.ai.handle_steer_left()
                    if(self.owner.world.graphic_engine.keyPressed('d')):
                        self.vehicle.ai.handle_aileron_right()
                        self.vehicle.ai.handle_rudder_right()
                        if self.owner.altitude<1:
                            self.vehicle.ai.handle_steer_right()
                    if(self.owner.world.graphic_engine.keyPressed('up')):
                        print('up')
                    if(self.owner.world.graphic_engine.keyPressed('down')):
                        print('down')
                    if(self.owner.world.graphic_engine.keyPressed('left')):
                        self.vehicle.ai.handle_throttle_down()
                    if(self.owner.world.graphic_engine.keyPressed('right')):
                        self.vehicle.ai.handle_throttle_up()
                else:
                    # ---- controls for ground vehicles ------------

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

            elif self.ai_vehicle_role=='gunner':
                if(self.owner.world.graphic_engine.keyPressed('a')):
                    self.vehicle_turret.ai.handle_rotate_left()

                if(self.owner.world.graphic_engine.keyPressed('d')):
                    self.vehicle_turret.ai.handle_rotate_right()

                if(self.owner.world.graphic_engine.keyPressed('f')):
                    self.vehicle_turret.ai.handle_fire()


        else:

            # ---- controls for walking around ------------

            action=False
            speed=self.get_calculated_speed()
            if(self.owner.world.graphic_engine.keyPressed('w')):
                self.owner.world_coords[1]-=speed*time_passed
                self.owner.rotation_angle=0
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('s')):
                self.owner.world_coords[1]+=speed*time_passed
                self.owner.rotation_angle=180
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('a')):
                self.owner.world_coords[0]-=speed*time_passed
                self.owner.rotation_angle=90
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('d')):
                self.owner.world_coords[0]+=speed*time_passed
                self.owner.rotation_angle=270
                self.owner.reset_image=True
                action=True
            if(self.owner.world.graphic_engine.keyPressed('f')):
                # fire the gun
                if self.primary_weapon!=None:
                    self.fire(self.owner.world.graphic_engine.get_mouse_world_coords(),self.primary_weapon)
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

    #---------------------------------------------------------------------------
    def handle_pickup_object(self,OBJECT_TO_PICKUP):
        ''' pickup object from the world '''
        # any distance calculation would be made before this function is called

        # reset ai 
        self.reset_ai()

        # double check the object is still there 
        if self.owner.world.check_object_exists(OBJECT_TO_PICKUP)==False:
            print('Debug object to pickup '+OBJECT_TO_PICKUP.name+' is no longer in the world')
        else:

            if OBJECT_TO_PICKUP.is_large_human_pickup:

                # need to make sure nobody else is already carrying it
                in_use=False
                for b in self.owner.world.wo_objects_human:
                    if b.ai.large_pickup==OBJECT_TO_PICKUP:
                        in_use=True

                if in_use:
                    print('Error large pick up is already picked up: ',OBJECT_TO_PICKUP.name)
                else:
                    self.large_pickup=OBJECT_TO_PICKUP
            else:
                if OBJECT_TO_PICKUP.is_gun:

                    # for now just pick up near by magazines (probably aren't any)
                    near_mags=self.handle_check_near_magazines(OBJECT_TO_PICKUP,50)
                    for b in near_mags:
                        self.handle_pickup_object(b)

                    # also loot any nearby containers
                    container=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_container,100)
                    if container!=None:
                        self.take_action_loot_container(container)

                self.speak('Picking up a '+OBJECT_TO_PICKUP.name)

                self.event_add_inventory(OBJECT_TO_PICKUP)
                # remove from world
                self.owner.world.remove_queue.append(OBJECT_TO_PICKUP)

    #---------------------------------------------------------------------------
    def handle_player_reload(self):
        ''' player reload. called by world when you press 'r' '''
        if self.primary_weapon!=None:
            self.handle_reload(self.primary_weapon)

    #---------------------------------------------------------------------------
    def handle_prone_state_change(self):
        '''if prone, stand up. If standing, go prone'''

        # reverse state
        self.prone=not self.prone

        if self.prone:
            self.owner.image_index=1
        else: 
            self.owner.image_index=0

        # good to do this as it changed
        self.owner.reset_image=True

        # add some fatigue, not sure how much
        self.fatigue+=15

    #-----------------------------------------------------------------------
    def handle_reload(self,weapon):
        '''reload weapon'''
        if weapon.is_gun:
            # first get the current magazine
            old_magazine=None
            if weapon.ai.magazine!=None:
                if weapon.ai.magazine.ai.removable:
                    old_magazine=weapon.ai.magazine

            # find a new magazine, sorting by size
            new_magazine=None
            biggest=0
            for b in self.inventory:
                if b.is_gun_magazine:
                    if weapon.name in b.ai.compatible_guns:
                        if len(b.ai.projectiles)>biggest:
                            new_magazine=b
                            biggest=len(b.ai.projectiles)

            # perform the swap 
            if old_magazine!=None:
                self.event_add_inventory(old_magazine)
                weapon.ai.magazine=None
            if new_magazine!=None:
                self.event_remove_inventory(new_magazine)
                weapon.ai.magazine=new_magazine
            else:
                self.speak("I'm out of ammo!")
                self.ai_want_ammo=True

        # at this point we should do a ai_mode change with a timer to simulate the 
        # reload time
        
        self.speak('reloading!')

    #-----------------------------------------------------------------------
    def handle_replenish_ammo(self):
        '''replenish ammo from a target object that we walked to'''
        if self.target_object==None:
            print('Error: replenish ammo from None target_object')
        else:
            if self.target_object.is_human:
                pass
            elif self.target_object.is_ammo_container:
                pass
            elif self.target_object.is_gun_magazine:
                pass
            elif self.target_object.is_container:
                pass

            # for now just cheat 
            for b in self.inventory:
                if b.is_gun_magazine:
                    engine.world_builder.load_magazine(self.owner.world,b)

            # load the magazine in the gun as well
            if self.primary_weapon!=None:
                if self.primary_weapon.ai.magazine!=None:
                    engine.world_builder.load_magazine(self.owner.world,self.primary_weapon.ai.magazine)

            self.ai_want_ammo=False

            print('debug: '+self.owner.name+' replenishing ammo')

    #--------------------------------------------------------------------------
    def handle_squad_actions(self):
        '''handle various squad decisions. returns true/false if an action was taken'''
        action=False
        if self.squad.squad_leader!=None:
            
            # are we the squad leader?
            if self.owner==self.squad.squad_leader:

                # check distance to destination 
                distance=engine.math_2d.get_distance(self.owner.world_coords,self.squad.destination)

                if distance>100:
                    self.ai_goal='move towards squad destination'
                    self.destination=self.squad.destination
                    self.ai_state='start_moving'
                    action=True
                    
            else:
                    
                # first we should check if we outrank the squad leader 
                        
                # check to see if we should get closer 
                distance_group=engine.math_2d.get_distance(self.owner.world_coords,self.squad.squad_leader.world_coords)
                if distance_group >self.squad_max_distance:
                    if self.prone:
                        self.handle_prone_state_change()
                    self.ai_goal='close_with_group'
                    self.destination=copy.copy(self.squad.squad_leader.world_coords)
                    self.time_since_ai_transition=0
                    self.ai_state='start_moving'

                    action=True
        else:
            # elect yourself as squad leader. Naturally!
            self.squad.squad_leader=self.owner
        return action
    
    #---------------------------------------------------------------------------
    def handle_squad_transportation_orders(self):
        '''assign transportation for the squad'''

        near_squad=self.owner.world.get_objects_within_range(self.owner.world_coords,self.squad.members,800)

        # remove yourself to prevent recursion
        near_squad.remove(self.owner)

        near_vehicle=self.owner.world.get_objects_within_range(self.owner.world_coords,self.owner.world.wo_objects_vehicle,1000)

        for b in near_vehicle:
            if len(near_squad)==0:
                break
            # calculate occupants
            occupants=len(b.ai.passengers)
            for c in self.owner.world.wo_objects_human:
                if c.ai.ai_goal=='enter_vehicle' and c.ai.target_object==b:
                    occupants+=1

            while occupants<b.ai.max_occupants:
                if len(near_squad)>0:
                    if near_squad[0].ai.in_vehicle:
                        #already in a vehicle, so no further action needed
                        near_squad.pop(0)
                    else:
                    # set this so they know where to go
                        if self.ai_vehicle_destination!=None:
                            near_squad[0].ai.ai_vehicle_destination=self.ai_vehicle_destination
                        near_squad[0].ai.react_asked_to_enter_vehicle(b)
                        occupants+=1
                        near_squad.pop(0)
                else:
                    break
        

    #---------------------------------------------------------------------------
    def handle_transfer(self,FROM_OBJECT,TO_OBJECT):
        '''transfer liquid/ammo/??? from one object to another'''
        

        if FROM_OBJECT.is_liquid and TO_OBJECT.is_container:
            source_amount=FROM_OBJECT.volume
            
            # add up total destination volume
            destination_amount=0
            for b in TO_OBJECT.ai.inventory:
                destination_amount+=b.volume

            # remember in containers this is considered a max volume    
            destination_maximum=TO_OBJECT.volume
            source_result,destination_result=engine.math_2d.get_transfer_results(source_amount,destination_amount,destination_maximum)
            FROM_OBJECT.volume=source_result
            
            # spawn a new liquid object with the amount to transfer
            z=engine.world_builder.spawn_object(self.owner.world,[0,0],FROM_OBJECT.name,False)
            z.volume=destination_result

            # add the new liquid to the container
            TO_OBJECT.add_inventory(z)
        else:
            print('error: handle_transfer error: src/dest not recognized!')

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

        # calling this by itself should remove all references to the object
        self.event_remove_inventory(selected)

    #---------------------------------------------------------------------------
    def launch_antitank(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man ''' 

        # standup. kneel would be better if it becomes an option later
        if self.prone:
            self.handle_prone_state_change()

        if self.antitank!=None:
            self.antitank.ai.fire(self.owner.world_coords,TARGET_COORDS)

            # drop the tube now that it is empty
            self.handle_drop_object(self.antitank)

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
    def react_asked_to_enter_vehicle(self,VEHICLE):
        '''react to the player asking the ai to enter the players vehicle'''
        if VEHICLE.ai.max_occupants<=len(VEHICLE.ai.passengers):
            self.speak('There is no where to sit!')
        else:
            if self.in_vehicle:
                print('error: bot asked to enter vehicle but already in a vehicle')
                self.speak("I'm already in a vehicle")
            else:
                distance=engine.math_2d.get_distance(self.owner.world_coords,VEHICLE.world_coords)

                if distance<1000:
                    self.take_action_enter_vehicle(VEHICLE,'ride along')
                    self.speak('Climbing onboard')   
                else:
                    self.speak('Too far') 

    #-----------------------------------------------------------------------
    def react_asked_to_exit_vehicle(self): 
        ''' react to being asked to exit the vehicle'''

        # could put some logic in here to keep crew memebers in the vehicle

        if self.in_vehicle:
            self.handle_exit_vehicle()
        else:
            print('error: asked to exit a vehicle, but not in a vehicle')
            self.speak("I'm not in a vehicle")

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
    def react_asked_to_wait(self,INTERVAL=60):
        self.ai_state='waiting'
        self.time_since_asked_to_wait=0
        self.wait_interval=INTERVAL
        self.speak("I'll wait for "+str(self.wait_interval))

    #-----------------------------------------------------------------------
    def reset_ai(self):
        '''resets all ai state variables'''

        # note this does NOT reset ai_wants

        self.ai_goal='none'
        self.ai_state='none'
        self.ai_vehicle_goal='none'
        self.target_object=None

    #-----------------------------------------------------------------------
    def take_action_enter_vehicle(self,VEHICLE,vehicle_goal='travel'):
        '''move to and enter vehicle'''

        # should check and see if we are trying to enter another vehicle

        if self.prone:
            self.handle_prone_state_change()


        # ask the driver to wait for us
        if VEHICLE.ai.driver!=None:
            # could specify a time based on how long we need to get there
            VEHICLE.ai.driver.ai.react_asked_to_wait()

        # head towards the vehicle
        # should check if the vehicle is hostile

        self.ai_vehicle_goal=vehicle_goal

        # this should have been set before this with the correct destination
        if self.ai_vehicle_destination==None:
            self.ai_vehicle_destination=self.squad.destination

        self.target_object=VEHICLE
        self.ai_goal='enter_vehicle'
        # not using copy here because vehicle may move
        self.destination=self.target_object.world_coords
        self.ai_state='start_moving'

        # tell the squad to mount up
        if self.owner==self.squad.squad_leader:
            self.handle_squad_transportation_orders()

    #-----------------------------------------------------------------------
    def take_action_get_ammo(self,NEAR):
        '''attempts to get ammo. returns True/False if it is successful'''
        if self.prone:
            self.handle_prone_state_change()

        # preference for ammo
        # 1 - ammo can
        # 2 - squad mate
        # 3 - ???

        # NEAR (bool) - keep distance to 500
        distance=2000
        if NEAR:
            distance=500
        
        best_ammo_can=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_ammo_container,distance)
        
        if best_ammo_can!=None:
            self.target_object=best_ammo_can
            self.ai_goal='get_ammo'
            self.destination=self.target_object.world_coords
            self.ai_state='start_moving'
            return True
        else:
            # do we have a squad buddy?
            best_squad_mate=None 
            if self.squad != None:
                if len(self.squad.members)>0:
                    best_squad_mate=self.owner.world.get_closest_object(self.owner.world_coords,self.squad.members,distance)

            if best_squad_mate != None:
                self.target_object=best_squad_mate
                self.ai_goal='get_ammo'
                self.destination=self.target_object.world_coords
                self.ai_state='start_moving'
                return True
            else: 
                # curious how often this happens
                print('debug:  - bot could not find ammo')
                return False

    #-----------------------------------------------------------------------
    def take_action_get_gun(self,NEAR,UPGRADE_ONLY):
        ''' attempts to get a gun. returns True/False if it is successful'''

        # thought - maybe the inventory add for guns should do the gun comparison instead of having it here

        # upgrade logic shoul be broken off into a think_ function and then this can be 
        # merged with take_action_get_item

        # NEAR : only look at guns in 500 range
        # UPGRADE_ONLY : only pickup a better gun (if you already have a gun)

        get_gun=False

        gun=None

        # NEAR (bool) - keep distance to 500
        distance=2000
        if NEAR:
            distance=500

        gun=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_guns,distance)

        if gun!=None:
            if UPGRADE_ONLY and self.primary_weapon!=None:
                ammo=self.handle_check_ammo(self.primary_weapon)

                #if there is no ammo in inventory and gun ammo is very low, just take it
                if ammo[1]==0 and ammo[0]<5:
                    get_gun=True
                elif self.primary_weapon.ai.type=='pistol' or self.primary_weapon.ai.type=='rifle':
                    # the thought here being that rifles are undesirable, and a mg is crew served and unlikely to 
                    # be picked up
                    if gun.ai.type in ['submachine gun','assault rifle','semi auto rifle']:
                        get_gun=True
            else:
                get_gun=True
            
        if get_gun:
            self.take_action_pickup_object(gun)
        
        return get_gun
            
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

        item=self.owner.world.get_closest_object(self.owner.world_coords,self.owner.world.wo_objects_container,distance) 

        if item==None:
            return False
        else:
            if self.prone:
                self.handle_prone_state_change()
            self.target_object=item
            self.ai_goal='loot_container'
            self.destination=self.target_object.world_coords
            self.ai_state='start_moving'
            self.speak("I'm going to check that "+item.name)
            return True
        
    #-----------------------------------------------------------------------
    def take_action_move_short_random_distance(self):
        distance=random.randint(50,200)

        if distance>70:
            if self.prone:
                self.handle_prone_state_change()

        self.destination=[self.owner.world_coords[0]+float(random.randint(-distance,distance)),self.owner.world_coords[1]+float(random.randint(-distance,distance))]
        self.ai_state='start_moving'
        self.ai_goal='short move'  

    #-----------------------------------------------------------------------
    def take_action_panic(self):

        # step down from squad lead. 
        # this keeps from leading the squad off the map 
        if self.squad.squad_leader==self.owner:
            self.squad.squad_leader=None

        if self.prone:
            self.handle_prone_state_change()

        # adrenaline effect. should allow the bot to run for a bit
        self.fatigue-=50

        self.destination=[self.owner.world_coords[0]+float(random.randint(-2300,2300)),self.owner.world_coords[1]+float(random.randint(-2300,2300))]
        self.ai_state='start_moving'
        self.ai_goal='panic'  
        self.speak('AAaaaaaaahhh!!!!')   

    #-----------------------------------------------------------------------
    def take_action_pickup_object(self,WORLD_OBJECT):
        '''move to and pick up an object'''

        if self.prone:
            self.handle_prone_state_change()

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
            self.reset_ai()
            self.speak('Got him !!')
        else:
            #target is alive, determine the best way to engage
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.target_object.world_coords)
            if distance>1500:
                print('debug : target ignored. target distance is'+str(distance))
                self.reset_ai()
            elif distance>300:
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
            # need to make sure we have a minimum distance to arm the weapon 
            if self.target_object.is_vehicle:
                if self.antitank!=None and DISTANCE<800:
                    self.launch_antitank(self.target_object.world_coords)
                    action=True
                    self.ai_want_antitank=True
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
                ammo=self.handle_check_ammo(self.primary_weapon)
                if ammo[0]>0:
                    # we can fire. this will be done automatically
                    action=True
                else:
                    if ammo[1]>0:
                        self.handle_reload(self.primary_weapon)
                        action=True
                    else:
                        self.ai_want_ammo=True

                        print('debug : thing_engage_close : out of ammo')
                        dm=self.owner.name
                        dm+=('\n  - weapon: '+self.primary_weapon.name)
                        dm+=('\n  -- ammo in gun: '+str(ammo[0]))
                        dm+=('\n  -- ammo in inventory: '+str(ammo[1]))
                        dm+=('\n  -- magazine count: '+str(ammo[2]))
                        print(dm)

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

        # should always go prone to make a smaller target for longer engagements
        if not self.prone:
            self.handle_prone_state_change()

        action=False # used locally to help with decision tree
        if self.target_object.is_vehicle:
            if self.antitank!=None and DISTANCE<800:
                self.launch_antitank(self.target_object.world_coords)
                action=True
                self.ai_want_antitank=True

        if action==False:
            if self.primary_weapon==None:
                # take an AT shot
                if self.antitank!=None and DISTANCE<800:
                    self.launch_antitank(self.target_object.world_coords)
                    action=True
                    self.ai_want_gun=True
                    self.ai_want_antitank=True
                else:
                    # engagement is far enough to risk going somewhere to get a gun ??? this needs to be re-thought
                    action=self.take_action_get_gun(False,False)
                    self.speak('Enemies spotted, need to get a gun!')
            # we have a primary weapon
            else:
                # check ammo (this is duplicated from think close. should be combined)
                ammo=self.handle_check_ammo(self.primary_weapon)
                if ammo[0]==0:
                    if ammo[1]>0:
                        self.handle_reload(self.primary_weapon)
                    else:
                        self.ai_want_ammo=True

                        self.reset_ai()
                else:
                    # check if target is too far 
                    if DISTANCE >self.primary_weapon.ai.range :
                        if self.prone:
                            self.handle_prone_state_change()
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

                # get a target 
                if action==False :
                    # get an enemy from the squad
                    self.target_object=self.get_target()
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
                
                # handle various squad actions
                action=self.handle_squad_actions()

                if action==False:
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

        action=False
        # check vehicle health, should we bail out ?
        if self.vehicle.ai.health<10:
            self.speak('Bailing Out!')
            self.handle_vehicle_died()
            # should probably let everyone else know
            action=True
        # check if we are close to our destination (if we have one)
        elif self.ai_vehicle_goal=='travel' or self.vehicle.ai.driver==self.owner:
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.ai_vehicle_destination)
            if distance<200:
                if self.vehicle.ai.current_speed<1:
                    # tell everyone to exit (including yourself)
                    for b in copy.copy(self.vehicle.ai.passengers):
                        b.ai.react_asked_to_exit_vehicle()
                    #self.handle_exit_vehicle()
                    action=True


        elif self.ai_vehicle_goal=='ride along':
            pass
        else:
            pass
            #print('Error - vehicle goal '+self.ai_vehicle_goal+' is not recognized')


        # basically if we haven't bailed out yet..
        if action==False:

            if self.vehicle.ai.driver==None:
                self.handle_change_vehicle_role('driver')

            if self.vehicle.ai.driver==self.owner:
                self.think_vehicle_drive()
                action=True

            # otherwise if we aren't driving, do we need to do something?

    #-----------------------------------------------------------------------
    def think_loot_container(self,CONTAINER):
        '''look at the contents of a container and take what we need'''
        # written for ai_container but will work for anything that has ai.inventory
        # getting to this function assumes that the bot is <5 from the container

        # reset AI 
        self.reset_ai()

        # make sure the object is still there
        if self.owner.world.check_object_exists(CONTAINER)==False:
            self.speak('Where did that '+CONTAINER.name+' go?')
        else:       
            medical_items=[]
            consumable_items=[]
            guns=[]
            grenades=[]
            anti_tank=[]
            gun_magazine=[]
            
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
                elif b.is_gun_magazine:
                    gun_magazine.append(b)

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
            
            # handle gun magazine decisions
            if len(gun_magazine)>0:
                gun=None

                # check if we are grabbing a gun
                for b in take:
                    if b.is_gun:
                        gun=b

                # if not, set it to the gun we have, if we have one
                if gun==None:
                    if self.primary_weapon!=None:
                        gun=self.primary_weapon

                # if we have a gun now, grab compatible magazines
                # only grab 2 magazines though
                grabbed=0
                if gun!=None:
                    for b in gun_magazine:
                        if gun.name in b.ai.compatible_guns:
                            if grabbed<2:
                                take.append(b)
                                grabbed+=1

            # take items!
            for c in take:
                CONTAINER.remove_inventory(c)
                self.event_add_inventory(c)
                self.speak('Grabbed a '+c.name)
            
    #-----------------------------------------------------------------------
    def think_move(self):
        ''' think about the current movement'''

        # ! note - the logic flow here needs to be re-done. 

        distance=engine.math_2d.get_distance(self.owner.world_coords,self.destination)

        # should we get a vehicle instead of hoofing it to wherever we are going?
        if distance>self.max_walk_distance:
            
            # failsafe. we don't want to be going on long trips when we have personal enemies (who are generally close)
            if len(self.personal_enemies)>0:
                self.think_generic()
            else:
                if self.ai_goal=='enter_vehicle':
                    #the vehicle we were trying to enter must have driven off, or something equally weird happened
                    print('error: vehicle inception! '+self.owner.name+' is in enter_vehicle state and distance to vehicle is '+str(distance))
                    # lets pause and rethink our priorities
                    self.reset_ai()

                # this should be the case most of the time
                else:
                    b=self.owner.world.get_closest_vehicle(self.owner,(self.max_walk_distance*0.6))
                    if b!=None:
                        # get_closest_vehicle only returns vehicles that aren't full

                        # won't return planes if not a pilot

                        # make the destination the vehicle destination so you will know where to go
                        self.ai_vehicle_destination=copy.copy(self.destination)

                        self.take_action_enter_vehicle(b)

                    else:
                        # no vehicles ? guess we are walking
                        pass
        else:
            # another fail safe to stop movement if we are possibly being attacked
            if distance >500 and len(self.personal_enemies)>0:
                self.think_generic()
                print('debug : '+self.owner.name+' blocked from moving '+str(distance)+' by personal enemy count: '+ str(len(self.personal_enemies)))
            else:
                self.think_move_close(distance)


    #-----------------------------------------------------------------------
    def think_move_close(self,DISTANCE):
        ''' think about movement when you are close to the objective'''
        # close is currently < self.max_walk_distance + no personal enemies
        # we are close to wherever we are going. don't worry about enemies too much

        if self.ai_goal=='pickup':
            if self.owner.world.check_object_exists(self.target_object):
                if DISTANCE<5:
                    self.handle_pickup_object(self.target_object)
            else:
                # object has been removed from world for whatever reason
                self.reset_ai()
          
        elif self.ai_goal=='loot_container':
            if DISTANCE<5:
                self.think_loot_container(self.target_object)

        elif self.ai_goal=='enter_vehicle':

            if self.owner.world.check_object_exists(self.target_object):

                # vehicles move around a lot so gotta check
                if self.destination!=self.target_object.world_coords:
                    self.destination=copy.copy(self.target_object.world_coords)
                    self.ai_state='start_moving'
                else:
                    if DISTANCE<5:
                        self.handle_enter_vehicle(self.target_object)
            else:
                # object has been removed from world for whatever reason
                self.reset_ai()

        elif self.ai_goal=='get_ammo':
            if DISTANCE<5:
                self.handle_replenish_ammo()
                self.reset_ai()
        elif self.ai_goal=='close_with_target':
            if self.owner.world.check_object_exists(self.target_object):
                # check if target is dead 
                if self.target_object.ai.health<1:
                    self.reset_ai()
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
            else:
                # object has been removed from world for whatever reason
                self.reset_ai()

        elif self.ai_goal=='close_with_group':
            if DISTANCE<self.squad_min_distance:
                self.ai_state='sleeping'
        elif self.ai_goal=='player_move':
            # this is initiated from world.select_with_mouse when
            # the selected object is too far away
            if DISTANCE<35:
                self.reset_ai()
                # basically disables the bot again. wait for player
                # interaction or another timeout
                self.time_since_player_interact=0
        else:
            #print('error: unhandled moving goal: '+self.ai_goal)
            # catchall for random moving related goals:
            if DISTANCE<5:
                self.reset_ai()

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
            ammo=self.handle_check_ammo(self.primary_weapon)
            # check if we have extra magazines in inventory
            # - if we don't then it is somewhat pointless to get more ammo
            if ammo[2]>0 :
                if ammo[1]<(ammo[0]):
                    # basically if we have less ammo in our inventory than in our gun
                    status=self.take_action_get_ammo(True)
            else:
                # no magazines, should we get a new gun?
                status=self.take_action_get_gun(True,False)


        return status

    #---------------------------------------------------------------------------
    def think_vehicle_drive(self):
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        if self.ai_state=='waiting':
            self.vehicle.ai.brake_power=1
            self.vehicle.ai.throtte=0
        else:
            if self.ai_vehicle_destination==None:
                print('debug: think_vehicle_drive ai_vehicle_destination==None')
                # determine vehicle destination
                self.ai_vehicle_destination=self.squad.destination
            
            # we want a tighter and more uniform time interval because we are 
            # actually driving here
            self.ai_think_rate=0.1

            # turn engines on
            # could do smarter checks here once engines have more stats
            need_start=False
            for b in self.vehicle.ai.engines:
                if b.ai.engine_on==False:
                    need_start=True
            if need_start:
                self.vehicle.ai.handle_start_engines()

            # get the rotation to the destination 
            r = engine.math_2d.get_rotation(self.vehicle.world_coords,self.ai_vehicle_destination)

            # compare that with the current vehicle rotation.. somehow?
            v = self.vehicle.rotation_angle

            if r>v:
                self.vehicle.ai.handle_steer_left()
                self.ai_think_rate=0.01
            if r<v:
                self.vehicle.ai.handle_steer_right()
                self.ai_think_rate=0.01
            
            # if its close just set it equal
            if r>v-1 and r<v+1:
                # neutral out steering 
                self.vehicle.ai.handle_steer_neutral()
                #self.vehicle.rotation_angle=r
                self.vehicle.reset_image=True

            if (r>355 and v<5) or (r<5 and v>355):
                # i think the rotation angle wrapping 360->0 and 0->360 is goofing stuff
                self.vehicle.ai.handle_steer_neutral()
                self.vehicle.rotation_angle=r
                print('debug - fixing 360 vehicle steering bug')

            distance=engine.math_2d.get_distance(self.owner.world_coords,self.ai_vehicle_destination)
            if distance<150:
                # apply brakes. bot will only exit when speed is zero
                self.vehicle.ai.throttle=0
                self.vehicle.ai.brake_power=1
            elif distance<500:
                self.vehicle.ai.throttle=0.5
                self.vehicle.ai.brake_power=0
            else:
                self.vehicle.ai.throttle=1
                self.vehicle.ai.brake_power=0


    #---------------------------------------------------------------------------
    def throw(self,TARGET_COORDS):
        ''' throw like you know the thing. cmon man '''   
        # stand up
        if self.prone:
            self.handle_prone_state_change() 
        if self.throwable!=None:
            #self.throwable.ai.throw(TARGET_COORDS)

            self.throwable.ai.thrown=True

            # set rotation and heading
            if self.owner.is_player :
                # do computations based off of where the mouse is. TARGET_COORDS is ignored
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.world.graphic_engine.get_player_screen_coords(),self.owner.world.graphic_engine.get_mouse_screen_coords())
            else :
                self.throwable.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,TARGET_COORDS)
                self.throwable.heading=engine.math_2d.get_heading_vector(self.owner.world_coords,TARGET_COORDS)

            self.handle_drop_object(self.throwable)

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            self.handle_death()
        else :

            # some unique vehicle stuff that needs to be applied to the player AND the AI
            # if this gets bigger it should get its own function
            if self.in_vehicle:
                if self.vehicle.ai.health<1:
                    #this needs to be here as there will exactly one update cycle if a vehicle dies
                    self.handle_vehicle_died()
                else:
                    self.update_human_vehicle_position()

            # might be faster to have a bool we could check
            if self.large_pickup!=None:
                self.large_pickup.world_coords=engine.math_2d.get_vector_addition(self.owner.world_coords,self.carrying_offset)
            
            # building awareness stuff. ai and human need this 
            self.time_since_building_check+=self.owner.world.graphic_engine.time_passed_seconds
            if self.time_since_building_check>self.building_check_rate:
                self.handle_building_check()


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
    def update_human_vehicle_position(self):
        '''update the humans position relative to the vehicle'''

        # coordinates + altitude
        self.owner.world_coords=copy.copy(self.vehicle.world_coords)
        self.owner.altitude=self.vehicle.altitude

        # rotate to match vehicle heading
        if self.vehicle.ai.open_top:
            if self.owner.rotation_angle!=self.vehicle.rotation_angle:
                self.owner.rotation_angle=self.vehicle.rotation_angle
                self.owner.reset_image=True
