'''
repo : https://github.com/openmarmot/twe

notes : dani the cat ai - upgraded with cat behaviors

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
            'task_pounce':self.update_task_pounce,
            'task_sleep':self.update_task_sleep,
        }

        self.memory={}
        self.memory['current_task']='task_think'

        self.speed=40

        # used to prevent repeats
        self.last_speak=''
        self.max_distance_to_interact_with_object=10
        self.last_meow_time=0
        self.pounce_target=None

    #---------------------------------------------------------------------------
    def speak(self,what):
        ''' cat meows and sounds '''
        if what !=self.last_speak:
            self.last_speak=what
            distance=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
            if distance<500:
                cat_sounds=['meow','mrrp','prrr','hiss','mew','purrrr','miao']
                s=f'[Dani] {random.choice(cat_sounds)}! ({what})'
                self.owner.world.text_queue.insert(0,s)

    #---------------------------------------------------------------------------
    def switch_task_move_to_location(self,destination,moving_object):
        '''switch task'''
        task_name='task_move_to_location'
        task_details = {
            'destination': copy.copy(destination),
            'moving_object': moving_object,
            'last_think_time': 0,
            'think_interval': 0.3
        }

        self.memory[task_name]=task_details
        self.memory['current_task']=task_name

        self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,destination)
        self.owner.reset_image=True   

    def switch_task_pounce(self,target):
        task_name='task_pounce'
        self.memory[task_name]={'target':target,'start_time':self.owner.world.world_seconds}
        self.memory['current_task']=task_name
        self.pounce_target=target

    def switch_task_sleep(self):
        task_name='task_sleep'
        self.memory[task_name]={'start_time':self.owner.world.world_seconds,'duration':random.randint(8,20)}
        self.memory['current_task']=task_name
        self.speed=0

    #---------------------------------------------------------------------------
    def switch_task_think(self):
        '''switch to task_think'''
        task_name='task_think'
        if task_name not in self.memory:
            self.memory[task_name]={}
        self.memory['current_task']=task_name
        self.speed=40

    #---------------------------------------------------------------------------
    def update(self):
        '''update '''
        if self.memory['current_task'] in self.memory and self.memory['current_task'] in self.task_map:
            self.task_map[self.memory['current_task']]()
        else:
            self.switch_task_think()

    #---------------------------------------------------------------------------
    def update_task_move_to_location(self):
        last_think_time=self.memory['task_move_to_location']['last_think_time']
        think_interval=self.memory['task_move_to_location']['think_interval']
        
        if self.owner.world.world_seconds-last_think_time>think_interval:
            self.memory['task_move_to_location']['last_think_time']=self.owner.world.world_seconds

            if self.memory['task_move_to_location']['moving_object'] is not None:
                self.memory['task_move_to_location']['destination']=copy.copy(self.memory['task_move_to_location']['moving_object'].world_coords)
                self.owner.rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,self.memory['task_move_to_location']['destination'])
                self.owner.reset_image=True

            distance=engine.math_2d.get_distance(self.owner.world_coords,self.memory['task_move_to_location']['destination'])

            if distance<self.max_distance_to_interact_with_object:
                self.memory.pop('task_move_to_location',None)
                self.switch_task_think()
                # playful meow on arrival
                if random.randint(0,3)==0:
                    self.speak('arrived dramatically')
        else:
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.speed,
                self.owner.world_coords,self.memory['task_move_to_location']['destination'],
                self.owner.world.time_passed_seconds)

    #---------------------------------------------------------------------------
    def update_task_pounce(self):
        if self.pounce_target is None or self.pounce_target not in self.owner.world.grid_square.wo_objects:
            self.switch_task_think()
            return
        dist=engine.math_2d.get_distance(self.owner.world_coords,self.pounce_target.world_coords)
        if dist<25:
            self.speak('pounced!')
            # knock over small things
            if hasattr(self.pounce_target,'is_consumable') and self.pounce_target.is_consumable:
                self.pounce_target.world_coords[0]+=random.randint(-30,30)
                self.pounce_target.world_coords[1]+=random.randint(-30,30)
            self.pounce_target=None
            self.switch_task_think()
        else:
            self.owner.world_coords=engine.math_2d.moveTowardsTarget(self.speed,
                self.owner.world_coords,self.pounce_target.world_coords,
                self.owner.world.time_passed_seconds)

    #---------------------------------------------------------------------------
    def update_task_sleep(self):
        task=self.memory.get('task_sleep',{})
        if self.owner.world.world_seconds-task.get('start_time',0)>task.get('duration',10):
            self.switch_task_think()
            self.speak('woke up from epic nap')
        else:
            self.speed=0

    #---------------------------------------------------------------------------
    def update_task_think(self):
        action=False
        now=self.owner.world.world_seconds

        # stay near player
        dist=engine.math_2d.get_distance(self.owner.world_coords,self.owner.world.player.world_coords)
        if dist>450:
            self.switch_task_move_to_location(self.owner.world.player.world_coords,self.owner.world.player)
            action=True

        # random meow
        if action is False and now-self.last_meow_time>random.randint(12,35):
            self.last_meow_time=now
            self.speak('random cat thought')
            action=True

        # pounce on nearby small objects
        if action is False and random.randint(0,4)==0:
            for obj in self.owner.grid_square.wo_objects:
                if obj.is_consumable or obj.name in ['small_flash','spark']:
                    d=engine.math_2d.get_distance(self.owner.world_coords,obj.world_coords)
                    if 20<d<180:
                        self.switch_task_pounce(obj)
                        action=True
                        break

        # occasional nap
        if action is False and random.randint(0,12)==0 and dist<300:
            self.switch_task_sleep()
            self.speak('time for nap')
            action=True

        if action is False:
            # zoomies or wander
            coords=[self.owner.world_coords[0]+random.randint(-900,900),self.owner.world_coords[1]+random.randint(-900,900)]
            self.switch_task_move_to_location(coords,None)
