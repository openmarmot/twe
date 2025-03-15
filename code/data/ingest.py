'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : 

just a simple script used to ingest data into the tables
'''


import sqlite3
import os
import shutil

# Data in array format





data = ['Kowalski', 'Nowak', 'Wiśniewski', 'Dąbrowski', 'Lewandowski', 'Wójcik', 'Kamiński', 'Kowalczyk', 'Zieliński', 'Szymański']


#------------------------------------------------------------------------------
def backup_database(db_file, backup_file):
    '''create a backup copy of a db file'''
    shutil.copy(db_file, backup_file)
    print(f"Backup successful: {backup_file}")
    

# Database file and backup file names
db_file = 'data.sqlite'
backup_file = db_file.split('.')[0]+'_backup.sqlite'

if os.path.exists(db_file):

    # Perform the backup
    backup_database(db_file, backup_file)


    # Connect to SQLite database
    conn = sqlite3.connect(db_file)


    # insert data
    cursor = conn.cursor()
    for b in data:
        try:
            cursor.execute('INSERT INTO names (ethnicity, name_type, name) VALUES (?, ?, ?)',('polish', 'last', b))
        except sqlite3.Error as e:
                    print(f"An error occurred: {e} while inputting value: ",b)

    # save data
    conn.commit()


    # Close connection
    conn.close()

    print('Database updated')
else:
    print(f"Database file {db_file} does not exist")