
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules
from random import randint, choice
#import custom packages
from ai.state import State
from engine.vector2 import Vector2
# module specific variables
module_version='0.0' #module software version
module_last_update_date='01-01-2016' #date of last update

#global variables

class AntStateHunting(State):

    def __init__(self, ant):

        State.__init__(self, "hunting")
        self.ant = ant
        self.got_kill = False

    def do_actions(self):

        spider = self.ant.world.get(self.ant.spider_id)

        if spider is None:
            return

        self.ant.destination = spider.location

        if self.ant.location.get_distance_to(spider.location) < 15:

            if randint(1, 5) == 1:
                spider.bitten()

                if spider.health <= 0:
                    self.ant.carry(self.ant.world.graphic_engine.images['bird'])
                    self.ant.world.remove_entity(spider)
                    self.got_kill = True


    def check_conditions(self):

        if self.got_kill:
            return "delivering"

        spider = self.ant.world.get(self.ant.spider_id)

        if spider is None:
            return "exploring"

        if spider.location.get_distance_to(self.ant.world.NEST_POSITION) > self.ant.world.NEST_SIZE * 3:
            return "exploring"

        return None

    def entry_actions(self):

        self.speed = 160 + randint(0, 50)

    def exit_actions(self):

        self.got_kill = False
