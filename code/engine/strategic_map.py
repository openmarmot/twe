
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
from ai.ai_bank import AIBank

#global variables


class StrategicMap(object):

    def __init__(self, graphics_engine):

        self.graphics_engine=graphics_engine

        

        self.map_squares=[]

        #banks {'bank name':bank object}
        self.banks={}

        # strategic AIs
        self.strategic_ai=[]
        self.strategic_ai.append(AIFactionStrategic(self,'german'))
        self.strategic_ai.append(AIFactionStrategic(self,'soviet'))
        self.strategic_ai.append(AIFactionStrategic(self,'american'))
        self.strategic_ai.append(AIFactionStrategic(self,'civilian'))

        # map offset 
        self.map_offset_x=350
        self.map_offset_y=75

        # save file name
        self.save_file_name=None

        # map size
        self.map_size=10
        
        self.strategic_menu=StrategicMenu(self)

    #---------------------------------------------------------------------------
    def advance_turn(self):
        '''have all the strategic ai take one turn and then update the map'''

        self.update_faction_budgets()

        for b in self.strategic_ai:
            b.advance_turn()
            self.update_map_data()

    #---------------------------------------------------------------------------
    def auto_resolve_battles(self):
        
        self.update_map_data()

        for map in self.map_squares:
            if map.map_control=='contested':
                germans_to_remove=0
                soviets_to_remove=0
                if map.german_count>map.soviet_count:
                    soviets_to_remove=map.soviet_count
                    germans_to_remove=random.randint(0,map.german_count)
                elif map.soviet_count>map.german_count:
                    germans_to_remove=map.german_count
                    soviets_to_remove=random.randint(0,map.soviet_count)
                else:
                    germans_to_remove=map.german_count
                    soviets_to_remove=map.soviet_count
                
                troops_to_remove=[]
                german_removed=0
                soviet_removed=0
                for b in map.map_objects:
                    if b.world_builder_identity.startswith('german') and german_removed<germans_to_remove:
                        troops_to_remove.append(b)
                        german_removed+=1
                    if b.world_builder_identity.startswith('soviet') and soviet_removed<soviets_to_remove:
                        troops_to_remove.append(b)
                        soviet_removed+=1

                for b in troops_to_remove:
                    map.map_objects.remove(b)


                if german_removed!=germans_to_remove or soviet_removed!=soviets_to_remove:
                    print('----')
                    print('troops to remove',len(troops_to_remove))
                    print('germans to remove',germans_to_remove)
                    print('german_removed',german_removed)
                    print('soviets to remove',soviets_to_remove)
                    print('soviet_removed',soviet_removed)
                    print('----')
                    for b in map.map_objects:
                        print('identity',b.world_builder_identity,'name: ',b.name)

                
        self.update_map_data()
            
    #---------------------------------------------------------------------------
    def create_banks(self):
        '''create banks for a new campaign'''

        # -- central state banks --

        bank=AIBank()
        bank.name='US Federal Reserve'
        bank.currencies_accepted=['US Dollar']
        bank.commodities_accepted=[]
        bank.factions_accepted=['american']
        bank.exchange_markup=0
        bank.accounts[0]={'US Dollar':1000000000}
        self.banks[bank.name]=bank

        bank=AIBank()
        bank.name='Reichsbank'
        bank.currencies_accepted=['German Reichsmark','German Military Script']
        bank.commodities_accepted=[]
        bank.factions_accepted=['german']
        bank.exchange_markup=0
        bank.accounts[0]={'German Reichsmark':1000000000}
        self.banks[bank.name]=bank

        bank=AIBank()
        bank.name='Gosbank'
        bank.currencies_accepted=['Soviet Ruble','Soviet Military Script']
        bank.commodities_accepted=[]
        bank.factions_accepted=['soviet']
        bank.exchange_markup=0
        bank.accounts[0]={'Soviet Ruble':1000000000}
        self.banks[bank.name]=bank

        # -- private or semi-private banks --

        bank=AIBank()
        bank.name='US Savings and Loan'
        bank.currencies_accepted=['US Dollar']
        bank.commodities_accepted=[]
        bank.factions_accepted=['american','civilian']
        bank.exchange_markup=0
        bank.accounts[0]={'US Dollar':1000000000}
        self.banks[bank.name]=bank

        bank=AIBank()
        bank.name='Volksbank'
        bank.currencies_accepted=['German Reichsmark','German Military Script']
        bank.commodities_accepted=[]
        bank.factions_accepted=['german','civilian']
        bank.exchange_markup=0
        bank.accounts[0]={'German Reichsmark':1000000000}
        self.banks[bank.name]=bank

        bank=AIBank()
        bank.name='Narodny Bank'
        bank.currencies_accepted=['Soviet Ruble','Soviet Military Script']
        bank.commodities_accepted=[]
        bank.factions_accepted=['soviet','civilian']
        bank.exchange_markup=0
        bank.accounts[0]={'Soviet Ruble':1000000000}
        self.banks[bank.name]=bank

        # the swiss !
        bank=AIBank()
        bank.name='Alpen Kreditbank'
        bank.currencies_accepted=['Soviet Ruble','German Reichsmark','US Dollar']
        bank.commodities_accepted=[]
        bank.factions_accepted=['german','soviet','civilian']
        bank.exchange_markup=0
        bank.accounts[0]={'Soviet Ruble':1000000000,'German Reichsmark':1000000000,'US Dollar':1000000000}
        self.banks[bank.name]=bank

    #---------------------------------------------------------------------------
    def create_map_squares(self):
        '''create the map squares and screen positions'''

        # get all the table names from the database
        map_names=self.get_map_names_from_tables()
            # Determine the number of squares per row (round up if it's not a perfect square)
        grid_size = math.ceil(math.sqrt(len(map_names)))

        # Create a 2D list to hold the grid squares
        grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Create grid square objects and assign them to grid positions
        for index, name in enumerate(map_names):
            y = index % grid_size
            x = index // grid_size
            spacing=85
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
        '''create a new campaign save file '''


        map_name=['A','B','C','D','E','F','G','H','I','J','K']
        # create the database
        conn = sqlite3.connect(self.save_file_name)
        cursor = conn.cursor()

        # generate the map tables
        for a in range(self.map_size):
            for b in range(self.map_size):
                table_name='map_'+map_name[a]+str(b)
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

        # - create the banks table -
        table_name='banks'
        create_table_sql = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            currencies_accepted TEXT,
            commodities_accepted TEXT,
            bank_internal_account TEXT,
            account_increment TEXT,
            exchange_markup TEXT,
            factions_accepted TEXT
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

        # - create the bank_accounts table -
        # currency_string 'currency1:amount,currency2:amount'
        table_name='bank_accounts'
        create_table_sql = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT,
            account_number TEXT,
            holdings TEXT
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
    def get_map_names_from_tables(self):
        # Connect to the SQLite database
        connection = sqlite3.connect(self.save_file_name)
        
        # Create a cursor object to execute SQL commands
        cursor = connection.cursor()
        
        # SQL query to get all table names
        # This query looks at the sqlite_master table where type is 'table'
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name LIKE 'map_%';
        """)
        
        # Fetch all results
        tables = cursor.fetchall()
        
        # Extract table names from the tuples returned by fetchall
        # remove the 'map_' prefix
        table_names = [table[0].replace('map_','') for table in tables]
        
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

        # sqlite connection
        conn = sqlite3.connect(self.save_file_name)
        cursor = conn.cursor()


        # create map squares
        self.create_map_squares()
        
        # -- load map square data --
        for map_square in self.map_squares:
            table_name='map_'+map_square.name
            
            select_all_sql = f"SELECT * FROM {table_name};"
            cursor.execute(select_all_sql)
            rows = cursor.fetchall()

            # Iterate through each row and create a new MapObject
            for row in rows:
                id, world_builder_identity, name, world_coords, rotation, inventory = row

                # Convert stored string data into correct formats
                world_coords = [float(world_coords.split(',')[0]),float(world_coords.split(',')[1])]
                rotation = float(rotation)
                # inventory will be '' in the db when it is empty. we want it to be [] not [''] 
                inventory = inventory.split(',') if inventory != '' else []

                # Create a new MapObject instance
                map_object = MapObject(world_builder_identity, name, world_coords, rotation, inventory)

                # Add the MapObject instance to the list
                map_square.map_objects.append(map_object)

        # update map data
        self.update_map_data()

        # -- load bank data --
        self.banks={}
        cursor.execute("SELECT * FROM banks;")
        rows=cursor.fetchall()
        for row in rows:
            (id,name,currencies_accepted,commodities_accepted
             ,bank_internal_account,account_increment,exchange_markup
             ,factions_accepted) = row
            
            bank=AIBank()
            bank.name=name
            bank.currencies_accepted=currencies_accepted.split(',')
            bank.commodities_accepted=commodities_accepted.split(',')
            bank.factions_accepted=factions_accepted.split(',')
            bank.exchange_markup=float(exchange_markup)
            bank.accounts={}
            self.banks[bank.name]=bank

        # -- load bank account data --
        cursor.execute("SELECT * FROM bank_accounts;")
        rows=cursor.fetchall()
        for row in rows:
            (id,bank_name,account_number,holdings) = row
            # convert the string back to a dictionary
            holdings_dict={}
            for data in holdings.split(','):
                data=data.split(':')
                holdings_dict[data[0]]=float(data[1])

            self.banks[bank_name].accounts[int(account_number)]=holdings_dict
        
        # -- strategic ai data ---
            

        
        # close sqlite connection
        conn.close()



         
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
        self.graphics_engine.switch_mode(1)

    #------------------------------------------------------------------------------
    def save_all_maps(self):
        ''' save all maps to sqlite'''

        conn = sqlite3.connect(self.save_file_name)
        cursor = conn.cursor()
        
        # iterate through each map and save map_objects to sqlite
        for map in self.map_squares:

            table_name='map_'+map.name

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
                world_coords= ','.join(str(item) for item in b.world_coords)
                rotation=str(b.rotation)
                inventory=','.join(str(item) for item in b.inventory)
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
        self.save_everything()

        print('----------------------')
        print('Good Bye!')

        # exit
        self.graphics_engine.quit=True

    #------------------------------------------------------------------------------
    def save_banks(self):
        ''' save banks and bank accounts'''

        conn = sqlite3.connect(self.save_file_name)
        cursor = conn.cursor()
        
        # - clear the data from the tables -
        tables_to_clear = ['banks', 'bank_accounts']
        delete_sql = "DELETE FROM {};"

        for table in tables_to_clear:
            cursor.execute(delete_sql.format(table))

        conn.commit()

        # save the banks
        for bank in self.banks.values():

            # - save the bank data -
            # data conversions. the table is all TEXT
            data = {
                'name': bank.name,
                'currencies_accepted': ','.join(str(item) for item in bank.currencies_accepted),
                'commodities_accepted': ','.join(str(item) for item in bank.commodities_accepted),
                'bank_internal_account': str(bank.bank_internal_account),
                'account_increment': str(bank.account_increment),
                'exchange_markup': str(bank.exchange_markup),
                'factions_accepted': ','.join(str(item) for item in bank.factions_accepted)
            }

            # Insert the data into the table
            insert_sql = '''
            INSERT INTO banks 
            (name, currencies_accepted, commodities_accepted, bank_internal_account, account_increment, exchange_markup, factions_accepted)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            '''

            cursor.execute(insert_sql, (
                data['name'], 
                data['currencies_accepted'], 
                data['commodities_accepted'], 
                data['bank_internal_account'], 
                data['account_increment'], 
                data['exchange_markup'], 
                data['factions_accepted']
            ))

            # Commit the changes
            conn.commit()

            # - save the account data -
            data_list=[]
            for account_number,data in bank.accounts.items():
                holdings=','.join(key+':'+str(value) for key,value in data.items())
                data_list.append(
                    {
                        'bank_name': bank.name,
                        'account_number': str(account_number),
                        'holdings': holdings
                    }
                )
            if len(data_list)>0:
                # SQL command to insert multiple rows
                insert_sql = '''
                INSERT INTO bank_accounts (bank_name, account_number, holdings)
                VALUES (?, ?, ?)
                '''

                # Preparing data for executemany
                rows = [(item['bank_name'], item['account_number'], item['holdings']) for item in data_list]

                cursor.executemany(insert_sql, rows)
                conn.commit()

                # Print how many rows were inserted
                #print(f"{cursor.rowcount} rows were inserted into {table_name}")

        # Close the connection
        conn.close()

    #---------------------------------------------------------------------------
    def save_everything(self):
        '''save all the campaign things'''
        self.save_all_maps()
        self.save_banks()

    #---------------------------------------------------------------------------
    def start_new_campaign(self):
        self.save_file_name=self.generate_save_filename()

        # create the sql database file
        self.create_new_save_file()

        # create map squares
        self.create_map_squares()

        # create banks
        self.create_banks()

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

        # save everything
        self.save_everything()
        
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
            self.save_everything()

            # reset strategic menus
            self.strategic_menu.change_menu('start')

            # switch to strategic mode
            self.graphics_engine.mode=2

    
    #---------------------------------------------------------------------------
    def update(self):
        pass

    #---------------------------------------------------------------------------
    def update_faction_budgets(self):
        # apply per faction stuff 
        for b in self.strategic_ai:
            if b.faction=='german':
                b.budget+=10
            elif b.faction=='soviet':
                b.budget+=12
            elif b.faction=='american':
                b.budget+=20
            elif b.faction=='civilian':
                b.budget+=1

        # sort all soldiers 
                
        # subtract maintenance for each soldier 
                
        # add budget for strategic resources
                

        

    #---------------------------------------------------------------------------
    def update_map_data(self):
        '''update map_square data that is map_object dependent'''
        # once all map objects are loaded, update the map control
        for b in self.map_squares:
            b.update_map_control()

        # it is important that map_control is updated on all maps before this is run
        for b in self.map_squares:
            b.update_hostile_count()

        # update the map features that result in letters being added to the map squares
        for b in self.map_squares:
            b.update_map_features()
