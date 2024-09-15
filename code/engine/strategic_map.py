
'''
module : module_template.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules
import random
import string
import sqlite3

#import custom packages
from engine.strategic_menu import StrategicMenu

#global variables


class StrategicMap(object):

    def __init__(self, graphics_engine):

        self.graphics_engine=graphics_engine

        self.strategic_menu=StrategicMenu(self)

        self.map_squares=[]

    #---------------------------------------------------------------------------
    def create_map_squares(self,map_size):
        '''create the map squares and screen positions'''

        # get all the table names from the database
        # sort names
        # create map squares
        # - table name
        # - screen coords 
        # - figure out who owns it
        pass

    #------------------------------------------------------------------------------
    def create_new_save_file(self,save_file_name,map_size):
        '''generate a map and create save file'''
        map_name=['A','B','C','D','E','F','G','H','I','J','K']
        # create the database
        conn = sqlite3.connect(save_file_name)
        cursor = conn.cursor()
        # generate the tables
        for a in range(map_size):
            for b in range(map_size):
                table_name=map_name[a]+str(b)
                # create table
                create_table_sql = f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    world_builder_identity INTEGER,
                    name TEXT NOT NULL,
                    world_coords TEXT,
                    rotation TEXT,
                    inventory TEXT
                );
                '''

                # Execute the SQL command to create the table
                try:
                    cursor.execute(create_table_sql)
                    # Commit the transaction
                    conn.commit()
                    print(f"Table '{table_name}' created successfully with an auto-incrementing ID.")
                except sqlite3.Error as e:
                    print(f"An error occurred: {e}")
                    # If an error occurs, rollback any changes
                    conn.rollback()

        # Close the connection
        conn.close()

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

    #------------------------------------------------------------------------------
    def load_world(self,map_coords,save_file):
        # get the current data for the map square

        # send to world_builder to spawn

        pass

    #------------------------------------------------------------------------------
    def save_world(self,world,save_file):
        '''saves the current world data'''


        # distribute objects that left the map to the appropriate map_square tables

        # clear the current map square table

        # save existing world objects to the current map square

        # world.reset() to wipe all the world array data

        pass

    #---------------------------------------------------------------------------
    def start_new_campaign(self):
        map_size=10
        save_file=self.generate_save_filename()

        # create the sql database file
        self.create_new_save_file(save_file,map_size)

        # create map squares
        self.create_map_squares(save_file)

        # generate initial troops

        # save all maps

    
    #---------------------------------------------------------------------------
    def update(self):
        pass
