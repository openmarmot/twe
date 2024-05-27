
'''
module : math_2d.py
language : Python 3.x
email : andrew@openmarmot.com
notes : 

basic name generator
'''


#import built in modules
import random
import sqlite3

#import custom packages


#global variables
german_names=[]
soviet_names=[]
polish_names=[]

# whether the data is loaded 
loaded=False

#------------------------------------------------------------------------------
def generate_names(ethnicity):
    # Connect to the SQLite database
    conn = sqlite3.connect('data/data.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM names WHERE ethnicity=? AND name_type='last'", (ethnicity,))    
    rows = cursor.fetchall()
    last_names = [row[0] for row in rows]

    cursor.execute("SELECT name FROM names WHERE ethnicity=? AND name_type='first'", (ethnicity,))

    rows = cursor.fetchall()
    first_names = [row[0] for row in rows]

    # Close the connection
    conn.close()

    names=[]
    for b in first_names:
        for c in last_names:
            names.append(b+' '+c)

    return names


#------------------------------------------------------------------------------
def load_data():
    global german_names
    global soviet_names
    global polish_names
    global loaded

    german_names=generate_names('german')
    soviet_names=generate_names('soviet')
    polish_names=generate_names('polish')

    loaded=True

    print('Name data load is complete')

#------------------------------------------------------------------------------
def get_name(ethnicity):
    '''get a random name'''
    global german_names
    global soviet_names
    global polish_names
    global loaded

    if loaded==False:
        load_data()

    if ethnicity=='german':
        return random.choice(german_names)
    elif ethnicity=='soviet':
        return random.choice(soviet_names)
    elif ethnicity=='civilian' or ethnicity=='polish':
        return random.choice(polish_names)