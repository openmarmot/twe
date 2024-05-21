
'''
module : math_2d.py
language : Python 3.x
email : andrew@openmarmot.com
notes : 

basic name generator
'''


#import built in modules
import random
#import custom packages


#global variables
last_german=['Müller', 'Schmidt', 'Bauer', 'Wagner', 'Becker', 'Hoffmann',
     'Richter', 'Schneider', 'Fischer', 'Meyer', 'Wolf', 'Becker', 'Schulz',
    'Konig', 'Weber', 'Klein', 'Krause']

first_german = ['Hans', 'Max', 'Michael', 'Felix', 'Klaus', 'Lukas', 'Markus',
     'Johanne', 'Matthias', 'Kurt', 'Gunther', 'Werner', 'Walther', 'Erich']

last_soviet = ['Ivanov', 'Smirnov', 'Kuznetsov', 'Popov', 'Sokolov',
     'Mikhailov', 'Novikov', 'Fedorov', 'Volkov', 'Kovalenko', 'Vasiliev']
first_soviet = ['Vladimir', 'Sergei', 'Ivan', 'Dmitri', 'Nikolai', 'Yuri', 'Mikhail', 'Alexei', 'Boris', 'Andrei']

first_polish = ['Adam', 'Michał', 'Krzysztof', 'Jan', 'Piotr', 'Tomasz', 'Marek', 'Bartłomiej', 'Jacek', 'Łukasz']
last_polish = ['Kowalski', 'Nowak', 'Wiśniewski', 'Dąbrowski', 'Lewandowski', 'Wójcik', 'Kamiński', 'Kowalczyk', 'Zieliński', 'Szymański']



#------------------------------------------------------------------------------
def generate(NAME_TYPE):
    '''generate a name of NAME_TYPE'''
    if NAME_TYPE=='german':
        return random.choice(first_german)+' '+random.choice(last_german)
    elif NAME_TYPE=='soviet':
        return random.choice(first_soviet)+' '+random.choice(last_soviet)
    elif NAME_TYPE=='civilian':
        return random.choice(first_polish)+' '+random.choice(last_polish)