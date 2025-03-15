'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :

'''

import copy
import random

import engine.math_2d

class AIDani():
    def __init__(self, owner):
        self.owner=owner

        self.task_map={
            'task_move_to_location':self.update_task_move_to_location,
            'task_think':self.update_task_think,
        }

        self.memory={}
        self.memory['current_task']='task_think'

        self.speed=0

        # used to prevent repeats
        self.last_speak=''
        self.max_distance_to_interact_with_object=10

    #---------------------------------------------------------------------------
    def speak(self,what):
        ''' say something if the ai is close to the player '''

        # simple way of preventing repeats
        if what !=self.last_speak:
            self.last_speak=what
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            if distance<400:
                s=f'[self.owner.name] {what}'
                self.owner.world.text_queue.insert(0,s)

    #---------------------------------------------------------------------------
    def switch_task_move_to_location(self,destination,moving_object):
        '''switch task'''
        # moving_object : optional game_object. set when we are moving to something that may move position
        # destination : this is a world_coords
        task_name='task_move_to_location'
        task_details = {
            'destination': copy.copy(destination),
            'moving_object': moving_object,
            'last_think_time': 0,
            'think_interval': 0.5
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,destination)
        # tell graphics engine to redo the image 
        self.owner.reset_image=True   

    #---------------------------------------------------------------------------
    def switch_task_think(self):
        '''switch to task_think'''
        task_name='task_think'

        if task_name in self.memory:
            # eventually will probably having something to update here
            pass
        else:
            # otherwise create a new one
            
            task_details = {
                'something': 'something'
            }

            self.memory[task_name]=task_details

        self.memory['current_task']=task_name

    #---------------------------------------------------------------------------
    def update(self):
        '''update '''

        # update the current task
        if self.memory['current_task'] in self.memory:
            if self.memory['current_task'] in self.task_map:
                # call the associated update function for the current task
                self.task_map[self.memory['current_task']]()
            else:
                engine.log.add_data('error','current task '+self.memory['current_task']+' not in task map',True)

        else:
            self.switch_task_think()

    #---------------------------------------------------------------------------
    def update_task_move_to_location(self):
        '''update task'''
        
        last_think_time=self.memory['task_move_to_location']['last_think_time']
        think_interval=self.memory['task_move_to_location']['think_interval']

        
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.memory['task_move_to_location']['last_think_time']=self.owner.world.world_seconds

            # if there is a moving object, reset the destination to match in case it moved
            if self.memory['task_move_to_location']['moving_object'] is not None:

                self.memory['task_move_to_location']['destination']=copy.copy(self.memory['task_move_to_location']['moving_object'].world_coords)
                # reset bot facing angle 
                self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.memory['task_move_to_location']['destination'])
                self.owner.reset_image=True

            # -- think about walking --
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.memory['task_move_to_location']['destination'])

            if distance<self.max_distance_to_interact_with_object:
                # we've arrived ! 
                self.memory.pop('task_move_to_location',None)
                self.switch_task_think()
        
        else:

            # -- walk --
            # move
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.speed,
                self.owner.world_coords,self.memory['task_move_to_location']['destination'],
                self.owner.world.time_passed_seconds)

    #---------------------------------------------------------------------------
    def update_task_think(self):
        '''task think - thinking about what to do next'''
        # the ugly function where we have to determine what we are doing

        # !! probably need to check the last time we were here so we aren't 
        # hitting this too often as it is likely computationally intense

        action=False
        
        # -- priorities --
        
        # -- check if we have older tasks to resume --
        # this is important for compound tasks 
        # all of this is todo for dani 
        if action is False:
            if 'task_enter_vehicle' in self.memory:
                self.memory['current_task']='task_enter_vehicle'
                action=True
            elif 'task_pickup_objects' in self.memory:
                self.memory['current_task']='task_pickup_objects'
                action=True
            elif 'task_loot_container' in self.memory:
                self.memory['current_task']='task_loot_container'
                action=True
            elif 'task_sit_down' in self.memory:
                self.memory['current_task']='task_sit_down'
                action=True

        # -- check if we are too far from player
        # this should be AFTER anything else important
        if action is False:
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            if distance>600:
                self.switch_task_move_to_location(self.owner.world.player.world_coords,self.owner.world.player)
                action=True

        # -- ok now we've really run out of things to do. do things that don't matter
        # ! NOTE Squad Lead will never get this far
        if action is False:
            # go for a walk
            coords=[self.owner.world_coords[0]+random.randint(-1400,1400),self.owner.world_coords[1]+random.randint(-1400,1400)]
            self.switch_task_move_to_location(coords,None)
