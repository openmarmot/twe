
'''
repo : https://github.com/openmarmot/twe

notes :

basic name generator. each ethnicity has a draw pool that is
shuffled once and then consumed, so a name is not repeated until
every name for that ethnicity has been used. civilian and polish
share one pool.
'''


#import built in modules
import random
import sqlite3

#import custom packages


#global variables
# full lists. draw pools are copied from these and consumed
german_names=[]
soviet_names=[]
polish_names=[]
german_draw=[]
soviet_draw=[]
polish_draw=[]

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

    if loaded==False:
        german_names=generate_names('german')
        soviet_names=generate_names('soviet')
        polish_names=generate_names('polish')
        refill(german_draw, german_names)
        refill(soviet_draw, soviet_names)
        refill(polish_draw, polish_names)

        loaded=True

        print('Name data load complete')
    else:
        print('Error: name data is already loaded')

#------------------------------------------------------------------------------
def refill(draw, source):
    '''fill draw with a shuffled copy of source'''
    draw.extend(source)
    random.shuffle(draw)

#------------------------------------------------------------------------------
def take_name(draw, source):
    '''pop a name. when the pool is empty, start a new shuffled cycle'''
    if len(draw)==0:
        refill(draw, source)
    return draw.pop()

#------------------------------------------------------------------------------
def get_name(ethnicity):
    '''get a random name that is not repeated until the pool restarts'''
    if ethnicity=='german':
        return take_name(german_draw, german_names)
    elif ethnicity=='soviet':
        return take_name(soviet_draw, soviet_names)
    elif ethnicity=='civilian' or ethnicity=='polish':
        return take_name(polish_draw, polish_names)
    

# init 
load_data()