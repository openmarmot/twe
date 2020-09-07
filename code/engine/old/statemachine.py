
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='June 13 2016' #date of last update

#global variables


class StateMachine(object):

    def __init__(self):

        self.states = {}
        self.active_state = None


    def add_state(self, state):

        self.states[state.name] = state


    def think(self):

        if self.active_state is None:
            return

        self.active_state.do_actions()

        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)


    def set_state(self, new_state_name):

        if self.active_state is not None:
            self.active_state.exit_actions()

        self.active_state = self.states[new_state_name]
        self.active_state.entry_actions()
