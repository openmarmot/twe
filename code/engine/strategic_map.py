
'''
module : module_template.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules
import random
import string

#import custom packages
from engine.strategic_menu import StrategicMenu
import engine.map_manager

#global variables


class StrategicMap(object):

    def __init__(self, graphics_engine):

        self.graphics_engine=graphics_engine

        self.strategic_menu=StrategicMenu(self)

        self.map_squares=[]


    

    

    #---------------------------------------------------------------------------
    def create_map_squares(self):
        '''create the map squares and screen positions'''

        # get all the table names from the database
        # sort names
        # create map squares
        # - table name
        # - screen coords 
        # - figure out who owns it
        pass

    #---------------------------------------------------------------------------
    def generate_save_filename(self,length=8):
        # Characters to choose from
        chars = string.ascii_letters + string.digits
        # Generate random part of the filename
        random_part = ''.join(random.choice(chars) for _ in range(length))
        # Combine with 'save' prefix
        return f"saves/save_{random_part}.sqlite"

    #---------------------------------------------------------------------------
    def handle_keydown(self,key):
        '''handle keydown events. called by graphics engine'''
        # these are for one off (not repeating) key presses

        #print('key ',KEY)
        self.strategic_menu.handle_input(key)

    #---------------------------------------------------------------------------
    def start_new_campaign(self):
        engine.map_manager.create_new_save_file(self.generate_save_filename())
    
    #---------------------------------------------------------------------------
    def update(self):
        pass
