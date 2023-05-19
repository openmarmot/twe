
'''
module : ai_group.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : AI that makes decisions for groups 
'''


#import built in modules
import random 
import copy

#import custom packages
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='May 17 2021' #date of last update


#global variables

class AISquad(object):
    def __init__(self,WORLD):

        self.world=WORLD
        # controls how fast the group world_coords moves. 
        # not sure what a good speed is
        self.speed=25

        # how far the ai will stray from the group before coming back
        self.max_distance=300

        # how close to the group a bot has to get before it can stop 'closing with group'
        self.min_distance=50

        # ai in the group will try to stay close to the group world coords
        # moves towards destination
        self.world_coords=[0.,0.]

        # destination - this is set by the faction tactical ai
        self.destination=[0.,0.]
        
        # people in the squad 
        # ai_human will remove itself on death 
        self.members=[] 

        # near enemies
        self.very_near_enemies=[]
        self.near_enemies=[]
        self.far_enemies=[]

        # faction - german/soviet/american/civilian
        self.faction='none'

        # a link back to the parent faction tactical
        # set in ai_faction_tactical.process_spawn_queue()
        # not used yet
        self.faction_tactical=None

        self.time_since_enemy_update=0.
        self.enemy_update_rate=0

        self.time_since_ai_think=0
        self.ai_think_rate=0

        # determines broadly how the ai behaves
        # normal - moves towards a destination set by ai_faction_tactical
        # guard - follows a world_object. possibly patrols around object
        # player - follows player
        self.ai_mode='normal'

    #---------------------------------------------------------------------------
    def add_to_squad(self, WORLD_OBJECT):
        ''' add a world_object to the squad. DOES NOT SPAWN AT THE MOMENT'''
        if WORLD_OBJECT.is_human==False:
            print('error: attempting to add a non human to squad')
        
        if WORLD_OBJECT.is_player:
            self.ai_mode='player'

        # remmove from the old squad
        if WORLD_OBJECT.ai.squad!=None:
            WORLD_OBJECT.ai.squad.members.remove(WORLD_OBJECT)    

        # add to this squad
        self.members.append(WORLD_OBJECT)

        # set squad var in ai
        WORLD_OBJECT.ai.squad=self

        # not sure what else we need to do

    #---------------------------------------------------------------------------
    def get_enemy(self):
        ''' return a enemy if one exists '''
        if len(self.very_near_enemies)>0:
            return self.very_near_enemies.pop()
        elif len(self.near_enemies)>0:
            # return last item in the list (and remove it from the list)
            return self.near_enemies.pop()
        elif len(self.far_enemies)>0:
            # return last item in the list (and remove it from the list)
            return self.far_enemies.pop()
        else:
            return None
    
    #---------------------------------------------------------------------------
    def handle_ai_think(self):
        ''' squad think. '''
        time_passed=self.world.graphic_engine.time_passed_seconds

        # think about the current mode. validate it and change as necessary 
        self.think_ai_mode()

        # check if squad position is wrong 
        self.think_position()

    #----------------------------------------------------------------------------
    def think_ai_mode(self):

        # check if the player is in the squad
        has_player=False
        for b in self.members:
            if b.is_player:
                has_player=True
        if has_player:
            self.ai_mode='player'
        else:
            # if in player mode reset to normal, otherwise do nothing
            if self.ai_mode=='player':
                self.ai_mode='normal'


        # reset min/max distances
        if self.ai_mode=='normal':
            if self.faction=='civilian':
                self.max_distance=3500
                self.min_distance=600
            else:
                self.max_distance=100
                self.min_distance=50
        elif self.ai_mode=='player':
            self.max_distance=80
            self.min_distance=30
        elif self.ai_mode=='guard':
            self.max_distance=100
            self.min_distance=30


    #----------------------------------------------------------------------------
    def think_position(self):
        # if we reset this too often the squads just kind of mill around
        # so better to make it distance based

        # note this interacts with max_distance in odd ways. if the bots are 
        # always within max distance then they will never move toward squad objectives
        # reseting the squad world_coords can make this worse


        d=engine.math_2d.get_distance(self.world_coords,self.members[0].world_coords)
        if d>(self.max_distance*2.75):
            # reset position to where the defacto squad lead is
            self.world_coords=copy.copy(self.members[0].world_coords)

            # reset speed to squad lead calculated speed + a bit so it doesn't get bogged down
            self.speed=self.members[0].ai.get_calculated_speed()*1.25
        


    #---------------------------------------------------------------------------
    def spawn_on_map(self):
        '''spawns the squad on the map at the squads world coords '''

        for b in self.members :
            # set the squad - i don't think this is set anywhere else
            b.ai.squad=self
            b.world_coords=[self.world_coords[0]+float(random.randint(-15,15)),self.world_coords[1]+float(random.randint(-15,15))]
            b.wo_start()

    #---------------------------------------------------------------------------
    def update(self):
        if len(self.members)>0:
            time_passed=self.world.graphic_engine.time_passed_seconds
            self.time_since_enemy_update+=time_passed
            self.time_since_ai_think+=time_passed
            
            # update enemy list on a random interval
            if self.time_since_enemy_update>self.enemy_update_rate:
                self.enemy_update_rate=random.uniform(0.3,3.5)
                self.time_since_enemy_update=0
                self.update_near_enemy_list()

            if self.time_since_ai_think>self.ai_think_rate:
                self.ai_think_rate=random.uniform(1.2,4.5)
                self.time_since_ai_think=0
                self.handle_ai_think()

            # -- handle squad movement --
            if self.ai_mode=='normal':
                self.world_coords=engine.math_2d.moveTowardsTarget(self.speed,self.world_coords,self.destination,time_passed)
            elif self.ai_mode=='guard':
                # if object to guard is stationary maybe walk a pattern around it
                # if object is human or vehicle maybe just stay close to it
                pass
            elif self.ai_mode=='player':
                self.world_coords=copy.copy(self.world.player.world_coords)
            else:
                print('error ai mode not recognized',self.ai_mode)
          


    #---------------------------------------------------------------------------
    def update_near_enemy_list(self):
        enemylist=[]
        self.near_enemies=[]
        self.very_near_enemies=[]
        self.far_enemies=[]
        if self.faction=='german':
            enemylist=self.world.wo_objects_soviet+self.world.wo_objects_american
        elif self.faction=='american':
            enemylist=self.world.wo_objects_soviet+self.world.wo_objects_german
        elif self.faction=='soviet':
            enemylist=self.world.wo_objects_german+self.world.wo_objects_american
        elif self.faction=='civilian':
            pass
        else:
            print('error! unknown squad faction!')
        
        for b in enemylist:
            d=engine.math_2d.get_distance(self.world_coords,b.world_coords)

            if d<500:
                self.very_near_enemies.append(b)
            elif d<850:
                self.near_enemies.append(b)
            elif d<1300:
                self.far_enemies.append(b)

            # enemies are close, stop movement for now 
            if len(self.members)>0 and (len(self.near_enemies)+len(self.very_near_enemies))>0:
                self.destination=copy.copy(self.members[0].world_coords)
                self.world_coords=copy.copy(self.destination)
                self.speed=0 # this will get reset on the next position update