
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
from datetime import datetime

#import custom packages
import engine.log
import engine.math_2d
import engine.world_builder
from engine.world import World
from engine.strategic_menu import StrategicMenu
from engine.map_square import MapSquare
from engine.map_object import MapObject
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

        # map offset 
        self.map_offset_x=400
        self.map_offset_y=150

        # save file name
        self.save_file_name=None

        # map size
        self.map_size=10

    #---------------------------------------------------------------------------
    def create_map_squares(self):
        '''create the map squares and screen positions'''

        # get all the table names from the database
        map_names=self.get_table_names(self.save_file_name)
            # Determine the number of squares per row (round up if it's not a perfect square)
        grid_size = math.ceil(math.sqrt(len(map_names)))

        # Create a 2D list to hold the grid squares
        grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Create grid square objects and assign them to grid positions
        for index, name in enumerate(map_names):
            y = index % grid_size
            x = index // grid_size
            spacing=70
            grid_square = MapSquare(name,[x*spacing+self.map_offset_x, y*spacing+self.map_offset_y])
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
    def create_new_save_file(self):
        '''generate a map and create save file'''
        map_name=['A','B','C','D','E','F','G','H','I','J','K']
        # create the database
        conn = sqlite3.connect(self.save_file_name)
        cursor = conn.cursor()
        # generate the tables
        for a in range(self.map_size):
            for b in range(self.map_size):
                table_name=map_name[a]+str(b)
                # create table
                create_table_sql = f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    world_builder_identity TEXT,
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
        
        # Get current date and time
        now = datetime.now()
        # Format the timestamp as YYYYMMDD_HHMMSS
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Combine with 'save' prefix, timestamp, and random part
        return f"saves/save_{timestamp}_{random_part}.sqlite"
    
    #---------------------------------------------------------------------------
    def generate_initial_civilians(self):

        for map in self.map_squares:
            map.map_objects+=engine.world_builder.generate_civilians(map.map_objects)

        # -- add some unique one offs --

        # big_cheese
        coords=[random.randint(-2000,2000),random.randint(-2000,2000)]
        rotation=random.randint(0,359)
        random.choice(self.map_squares).map_objects.append(MapObject('big_cheese','big_cheese',coords,rotation,[]))

        # shovel_man
        coords=[random.randint(-2000,2000),random.randint(-2000,2000)]
        rotation=random.randint(0,359)
        random.choice(self.map_squares).map_objects.append(MapObject('shovel_man','shovel_man',coords,rotation,[]))
    
    #---------------------------------------------------------------------------
    def generate_initial_map_features(self):
        '''generate map feature placement'''

        # i think we also need to generate the features themselves
        # after that they get saved automatically when the map is saved?
        # and then maybe the list of objects for the map gets checked on 
        # load for airports or whatever and the bools get flipped to true?

        west_column=[]
        east_column=[]
        north_row=self.map_squares[:self.map_size]
        south_row=self.map_squares[-self.map_size:]

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

        # towns 
        for _ in range(20):
            random.choice(self.map_squares).town=True

        # set inital map control 
        # german
        for b in west_column:
            b.image_index=2
            b.map_control='german'
        # soviet
        for b in east_column:
            b.image_index=1
            b.map_control='soviet'

    #---------------------------------------------------------------------------
    def generate_initial_map_objects(self):
        '''generate objects for the map features'''

        for map in self.map_squares:
            map_area_count=0
            if map.rail_yard:
                map_area_count+=1
            if map.airport:
                map_area_count+=1
            if map.town:
                map_area_count+=1

            if map_area_count>0:
                coord_list=engine.math_2d.get_random_constrained_coords([0,0],6000,5000,map_area_count)

                if map.rail_yard:
                    coords=coord_list.pop()
                    name='Rail Yard' # should generate a interessting name
                    map.map_objects+=engine.world_builder.generate_world_area(coords,'rail_yard',name)
                if map.airport:
                    coords=coord_list.pop()
                    name='Airport' # should generate a interessting name
                    map.map_objects+=engine.world_builder.generate_world_area(coords,'airport',name)
                if map.town:
                    coords=coord_list.pop()
                    name='Town' # should generate a interessting name
                    map.map_objects+=engine.world_builder.generate_world_area(coords,'town',name)

            # generate clutter
            map.map_objects+=engine.world_builder.generate_clutter(map.map_objects)

    #------------------------------------------------------------------------------
    def generate_initial_units(self):
        '''generate and place the inital units for each side'''
        
        # might eventually move this data out to sqlite
        for b in self.strategic_ai:
            if b.faction=='german':
                squads=['German 1944 Rifle'] * 40
                squads+=['German 1944 Panzergrenadier Mech'] * 20
                squads+=['German 1944 Fallschirmjager'] * 5

                b.set_initial_units(squads)
            elif b.faction=='soviet':
                squads=['Soviet 1943 Rifle'] * 60
                squads+=['Soviet 1944 SMG'] * 5
                squads+=['Soviet 1944 Rifle Motorized'] * 5

                b.set_initial_units(squads)
            elif b.faction=='american':
                # not setup to handle this yet
                pass


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

    #---------------------------------------------------------------------------
    def load_campaign_from_save(self,save_file_name):
        '''load a campaign from file and initialize strategic map'''
        self.save_file_name=save_file_name

        # create map squares
        self.create_map_squares()

        # load in map_objects from sql

        # update map data
        self.update_map_data()

         
    #------------------------------------------------------------------------------
    def load_world(self,map_square,spawn_faction):
        '''handles handoff from strategic map to world mode and loads a map->world'''

        # create a fresh world 
        self.graphics_engine.world=World()

        # set the map name so we can unload it to the correct map when we are done playing
        self.graphics_engine.world.map_square_name=map_square.name

        # send to world_builder to convert map_objects to world_objects (this spawns them)
        engine.world_builder.load_world(self.graphics_engine.world,map_square.map_objects,spawn_faction)

        # clear maps?

        # switch to world mode
        self.graphics_engine.mode=1

    #------------------------------------------------------------------------------
    def save_all_maps(self):
        ''' save all maps to sqlite'''

        conn = sqlite3.connect(self.save_file_name)
        cursor = conn.cursor()
        
        # iterate through each map and save map_objects to sqlite
        for map in self.map_squares:

            table_name=map.name

            # clear table data first 
            # SQL to delete all rows from the table
            delete_sql = '''
            DELETE FROM {table};
            '''.format(table=table_name)

            cursor.execute(delete_sql)
            conn.commit()
            
            # build the data list from map_objects
            data_list=[]
            for b in map.map_objects:

                # string conversions
                world_coords= ', '.join(str(item) for item in b.world_coords)
                rotation=str(b.rotation)
                inventory=', '.join(str(item) for item in b.inventory)
                data_list.append(
                    {
                        'world_builder_identity': b.world_builder_identity,
                        'name': b.name,
                        'world_coords': world_coords,
                        'rotation': rotation,
                        'inventory': inventory
                    }
                )
            if len(data_list)>0:
                # SQL command to insert multiple rows
                insert_sql = '''
                INSERT INTO {table} (world_builder_identity, name, world_coords, rotation, inventory)
                VALUES (?, ?, ?, ?, ?)
                '''.format(table=table_name)

                # Preparing data for executemany
                rows = [(item['world_builder_identity'], item['name'], item['world_coords'], 
                        item['rotation'], item['inventory']) for item in data_list]

                cursor.executemany(insert_sql, rows)
                conn.commit()

                # Print how many rows were inserted
                #print(f"{cursor.rowcount} rows were inserted into {table_name}")

        # Close the connection
        conn.close()
    
    #------------------------------------------------------------------------------
    def save_and_exit_game(self):
        '''saves all maps and exits game'''

        # by the time you get here the world is already unloaded.

        # one more save all
        self.save_all_maps()

        print('----------------------')
        print('Good Bye!')

        # exit
        self.graphics_engine.quit=True

    #---------------------------------------------------------------------------
    def start_new_campaign(self):
        self.save_file_name=self.generate_save_filename()

        # create the sql database file
        self.create_new_save_file()

        # create map squares
        self.create_map_squares()

        # generate initial map features
        self.generate_initial_map_features()

        # generate map objects for the features
        self.generate_initial_map_objects()

        # generate initial civilian pop
        self.generate_initial_civilians()

        # decide on and place initial troops
        self.generate_initial_units()

        # update map data
        self.update_map_data()

        # save all maps
        self.save_all_maps()   
        
        # load specific map player is in 

    #------------------------------------------------------------------------------
    def unload_world(self):  
        '''unload world to the correct map_square and make the transition to the strategic map'''
        
        # determine what map_square was represented by the loaded world
        map_square=None
        for b in self.map_squares:
            if b.name==self.graphics_engine.world.map_square_name:
                map_square=b
                break
                
        if map_square==None:
            engine.log.add_data('error','strategic_map.unload_world: world.map_square_name unknown: '+
                self.graphics_engine.world.map_square_name,True)
        else:
            # unload world objects into the map square
            engine.world_builder.convert_world_objects_to_map_objects(self.graphics_engine.world,map_square)

            # process objects that left the map

            # update map data everywhere
            self.update_map_data()

            # save everything
            self.save_all_maps()

            # reset strategic menus
            self.strategic_menu.change_menu('start')

            # switch to strategic mode
            self.graphics_engine.mode=2


    
    #---------------------------------------------------------------------------
    def update(self):
        pass
    
    #---------------------------------------------------------------------------
    def update_map_data(self):
        '''update map_square data that is map_object dependent'''
        # once all map objects are loaded, update the map control
        for b in self.map_squares:
            b.update_map_control()

        # once the map control is updated everywhere, update hostile count 
        for b in self.map_squares:
            b.update_hostile_count()
