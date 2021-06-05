
'''
module : db_interface.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : 

static module for interfacing with sqllite db
- create tables
- import and export data to tables


# ref
https://www.pythoncentral.io/introduction-to-sqlite-in-python/
'''


#import built in modules
import copy 
import sqlite3

#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='june 05 2021' #date of last update


#------------------------------------------------------------------------------
def clear_map_world_object(MAP_X,MAP_Y):
    ''' delete all data for the current map in the world_object table
         in prep for saving new info'''




#------------------------------------------------------------------------------
def create_new_world(DATABASE_NAME):
    ''' a world is a sqllite database with multiple tables '''
    # DATABASE_NAME - this file should not already exist
    
    name='data/'+DATABASE_NAME
    
    # create database 
    db = sqlite3.connect(name)

    cursor = db.cursor()

    # create world_object table 
    cursor.execute('''
        CREATE TABLE world_object(id INTEGER PRIMARY KEY, name TEXT,
        world_builder_identity TEXT, faction TEXT, map_x INTEGER, map_y INTEGER)
    ''')

    db.commit()
    db.close()


#------------------------------------------------------------------------------
def get_map_world_objects(MAP_X,MAP_Y):
    ''' return a list of comma delineated strings representing rows 
        that match the MAP coords from the world_objects table '''
    