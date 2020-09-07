
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
module_last_update_date='June 13 2016' #date of last update

#global variables


class AntStateExploring(State):

    def __init__(self, ant):

        State.__init__(self, "exploring")
        self.ant = ant

    def random_destination(self):

        w, h = self.ant.world.SCREEN_SIZE
        self.ant.destination = Vector2(randint(0, w), randint(0, h))

    def do_actions(self):

        if randint(1, 20) == 1:
            self.random_destination()

    def check_conditions(self):

        leaf = self.ant.world.get_close_entity("leaf", self.ant.location)
        if leaf is not None:
            self.ant.leaf_id = leaf.id
            return "seeking"

        spider = self.ant.world.get_close_entity("spider", self.ant.world.NEST_POSITION, self.ant.world.NEST_SIZE)
        if spider is not None:
            if self.ant.location.get_distance_to(spider.location) < 100:
                self.ant.spider_id = spider.id
                return "hunting"

        return None

    def entry_actions(self):

        self.ant.speed = 120. + randint(-30, 30)
        self.random_destination()
