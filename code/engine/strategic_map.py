
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
import math

#import custom packages
from engine.strategic_menu import StrategicMenu
from engine.map_square import MapSquare
from ai.ai_faction_strategic import AIFactionStrategic

#global variables


class StrategicMap(object):

    def __init__(self, graphics_engine):

        self.graphics_engine=graphics_engine

        self.strategic_menu=StrategicMenu(self)

        self.map_squares=[]

        # strategic AIs
        self.strategic_ai=[]
        self.strategic_ai.append(AIFactionStrategic(self,'german'))
        self.strategic_ai.append(AIFactionStrategic(self,'soviet'))
        self.strategic_ai.append(AIFactionStrategic(self,'american'))
        self.strategic_ai.append(AIFactionStrategic(self,'civilian'))

    #---------------------------------------------------------------------------
    def create_map_squares(self,save_file_name):
        '''create the map squares and screen positions'''

        # get all the table names from the database
        map_names=self.get_table_names(save_file_name)
            # Determine the number of squares per row (round up if it's not a perfect square)
        grid_size = math.ceil(math.sqrt(len(map_names)))

        # Create a 2D list to hold the grid squares
        grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Create grid square objects and assign them to grid positions
        for index, name in enumerate(map_names):
            y = index % grid_size
            x = index // grid_size
            spacing=70
            grid_square = MapSquare(name,[x*spacing+250, y*spacing+150])
            grid[y][x] = grid_square
        
        # Assign neighbors (above, below, left, right)
        for y in range(grid_size):
            for x in range(grid_size):
                grid_square = grid[y][x]
                if grid_square is None:
                    continue  # Skip empty grid spaces if map_names does not fill entire grid
                
                # Above
                if y > 0:
                    grid_square.north = grid[y - 1][x]
                # Below
                if y < grid_size - 1 and grid[y + 1][x] is not None:
                    grid_square.south = grid[y + 1][x]
                # Left
                if x > 0:
                    grid_square.west = grid[y][x - 1]
                # Right
                if x < grid_size - 1 and grid[y][x + 1] is not None:
                    grid_square.east = grid[y][x + 1]

        # Flatten the grid and return the list of GridSquare objects
        self.map_squares=[square for row in grid for square in row if square is not None]
    

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
    def generate_initial_map_features(self,map_size):
        '''generate map feature placement'''

        # i think we also need to generate the features themselves
        # after that they get saved automatically when the map is saved?
        # and then maybe the list of objects for the map gets checked on 
        # load for airports or whatever and the bools get flipped to true?

        west_column=[]
        east_column=[]
        north_row=self.map_squares[:map_size]
        south_row=self.map_squares[-map_size:]

        for b in self.map_squares:
            if b.name[0]=='A':
                west_column.append(b)
            # this needs to be fixed for bigger maps
            if b.name[0]=='J':
                east_column.append(b)



        # airports
        random.choice(west_column).airport=True
        random.choice(east_column).airport=True
        random.choice(self.map_squares).airport=True

        # rail yards
        random.choice(west_column).rail_yard=True
        random.choice(east_column).rail_yard=True
        random.choice(north_row).rail_yard=True
        random.choice(south_row).rail_yard=True


        # set inital map control 
        # german
        for b in west_column:
            b.image_index=2
        # soviet
        for b in east_column:
            b.image_index=1


    
    #---------------------------------------------------------------------------
    def get_table_names(self,db_file_path):
        # Connect to the SQLite database
        connection = sqlite3.connect(db_file_path)
        
        # Create a cursor object to execute SQL commands
        cursor = connection.cursor()
        
        # SQL query to get all table names
        # This query looks at the sqlite_master table where type is 'table'
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%';
        """)
        
        # Fetch all results
        tables = cursor.fetchall()
        
        # Extract table names from the tuples returned by fetchall
        table_names = [table[0] for table in tables]
        
        # Close the connection
        connection.close()
        return table_names

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

        # generate initial map features
        self.generate_initial_map_features(map_size)

        # generate initial troops
        for b in self.strategic_ai:
            b.set_initial_units()

        # save all maps
            
    
    #---------------------------------------------------------------------------
    def update(self):
        pass
