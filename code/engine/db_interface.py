
'''
module : db_interface.py
language : Python 3.x
email : andrew@openmarmot.com
notes : 

static module for interfacing with sqllite db
- create tables
- import and export data to tables


# ref
https://www.pythoncentral.io/introduction-to-sqlite-in-python/

!!!!!! Note --- this is old code and is probably going to be deleted


'''


#import built in modules
import copy 
import sqlite3

#import custom packages


#------------------------------------------------------------------------------
def clear_map_world_object(MAP_X,MAP_Y):
    ''' delete all data for the current map in the world_object table
         in prep for saving new info'''




#------------------------------------------------------------------------------
def create_new_world(DATABASE_NAME):
    ''' a world is a sqllite database with multiple tables '''
    # DATABASE_NAME - this file should not already exist
    
    name='data/'+DATABASE_NAME
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
def select_map_world_objects(DATABASE_NAME,MAP_X,MAP_Y):
    ''' return a list of comma delineated strings representing rows 
        that match the MAP coords from the world_objects table '''

    name='data/'+DATABASE_NAME
    db = sqlite3.connect(name)
    cursor = db.cursor()

    db.commit()
    db.close()


#------------------------------------------------------------------------------
def insert_world_objects(DATABASE_NAME,OBJECTS):
    ''' insert a list of world objects '''
    # format 
    # OBJECTS=[(name,world_builder_identity,faction,map_x,map_y)]
    name='data/'+DATABASE_NAME
    db = sqlite3.connect(name)
    cursor = db.cursor()
    cursor.executemany(''' INSERT INTO world_object(name,world_builder_identity,faction,map_x,map_y) VALUES(?,?,?,?,?)''', OBJECTS)
    db.commit()
    db.close()