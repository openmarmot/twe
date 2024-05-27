'''
module : ingest.py
language : Python 3.x
email : andrew@openmarmot.com
notes : 

testing area for queries 
'''

import sqlite3

#------------------------------------------------------------------------------
def generate_names(ethnicity):
    # Connect to the SQLite database
    conn = sqlite3.connect('data.sqlite')
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

print(generate_names('german'))
