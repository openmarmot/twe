
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

        # ai in the group will try to stay close to the group world coords
        # moves towards destination
        self.world_coords=[0.,0.]

        # destination - this is set by the faction tactical ai
        self.destination=[0.,0.]
        
        # people in the squad 
        # ai_human will remove itself on death 
        self.members=[] 

        # near enemies
        self.near_enemies=[]

        # faction - german/soviet/american/civilian
        self.faction='none'

        self.time_since_enemy_update=0.
        self.enemy_update_rate=0

        self.time_since_ai_think=0
        self.ai_think_rate=0

        # determines broadly how the ai behaves
        # normal - moves towards a destination
        # guard - follows a world_object
        # player - same as guard? only guarding the player?
        self.ai_mode='normal'

    #---------------------------------------------------------------------------
    def add_to_squad(self, WORLD_OBJECT):
        ''' add a world_object to the squad. DOES NOT SPAWN AT THE MOMENT'''
        if WORLD_OBJECT.is_human==False:
            print('error: attempting to add a non human to squad')
        
        if WORLD_OBJECT.is_player:
            self.ai_mode='player'

        WORLD_OBJECT.ai.squad=self

        # not sure what else we need to do

    #---------------------------------------------------------------------------
    def get_enemy(self):
        ''' return a enemy if one exists '''

        if len(self.near_enemies)>0:
            # return last item in the list (and remove it from the list)
            return self.near_enemies.pop()
        else:
            return None
    
    #---------------------------------------------------------------------------
    def handle_ai_think(self):
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        if self.ai_mode=='normal':
            self.world_coords=engine.math_2d.moveTowardsTarget(self.speed,self.world_coords,self.destination,time_passed)
        elif self.ai_mode=='guard':
            # if object to guard is stationary maybe walk a pattern around it
            # if object is human or vehicle maybe just stay close to it
            pass
        elif self.ai_mode=='player':
            self.world_coords=copy.copy(self.world.player.world_coords)

    #---------------------------------------------------------------------------
    def spawn_on_map(self):
        '''spawns the squad on the map at the squads world coords '''

        if self.faction=='civilian':
            print('setting max_distance for civ squad')
            self.max_distance=1000

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
                self.handle_ai_think
          


    #---------------------------------------------------------------------------
    def update_near_enemy_list(self):
        enemylist=[]
        self.near_enemies=[]
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
            if d<1200:
                self.near_enemies.append(b)
                if d<800:
                    # enemies are close, stop movement for now 
                    if len(self.members)>0:
                        self.destination=copy.copy(self.members[0].world_coords)
                        self.world_coords=copy.copy(self.destination)