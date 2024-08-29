'''
module : engine/penetration_calculator.py
language : Python 3.x
email : andrew@openmarmot.com
notes : map related stuff. mostly sql ?
'''

#import built in modules
import sqlite3

#------------------------------------------------------------------------------
def create_new_save_file(save_file_name):
    '''generate a map and create save file'''
    map_size=10
    map_name=['A','B','C','D','E','F','G','H','I','J','K']
    map_squares=[]
    # create the database
    conn = sqlite3.connect(save_file_name)
    cursor = conn.cursor()
    # generate the tables
    for a in range(map_size):
        for b in range(map_size):
            table_name=map_name[a]+str(b)
            map_squares.append(table_name)
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

    # generate maps 
    for b in map_squares:
        # spawn all world objects

        # something something

        #save_world(world,save_file_name)
        pass


        

#------------------------------------------------------------------------------
def load_world(map_coords,save_file):
    # get the current data for the map square

    # send to world_builder to spawn

    pass

#------------------------------------------------------------------------------
def save_world(world,save_file):
    '''saves the current world data'''


    # distribute objects that left the map to the appropriate map_square tables

    # clear the current map square table

    # save existing world objects to the current map square

    # world.reset() to wipe all the world array data

    pass