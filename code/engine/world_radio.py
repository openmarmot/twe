'''
module : engine/world_radio.py
language : Python 3.x
email : andrew@openmarmot.com
notes : handles the radio simulation
'''

import engine.log

channels={}
# key : frequency
# value : [] array of radios

#---------------------------------------------------------------------------
def add_radio(frequency,radio):
    '''add a radio to the correct frequency channel'''
    # this is called by ai_radio
    global channels
    remove_radio(radio)
    if frequency in channels:
        channels[frequency].append(radio)
    else:
        engine.log.add_data('warn','world_radio.add_radio frequency channel '+str(frequency)+' does not exist',True)

#---------------------------------------------------------------------------
def remove_radio(radio):
    '''remove a radio from all channels'''
    # this is called by ai_radio
    global channels
    for r in channels.values():
        if radio in r:
            r.remove(radio)

#---------------------------------------------------------------------------
def load(world):
    global channels
    channels={}
    channels[world.german_ai.radio_frequency]=[]
    channels[world.soviet_ai.radio_frequency]=[]
    channels[world.american_ai.radio_frequency]=[]
    channels[world.civilian_ai.radio_frequency]=[]

    # I think eventually vehicles and squads may split out?
    # germans definitely had a different frequency for tanks


#---------------------------------------------------------------------------
def send_message(frequency,message):
    # frequency : should match a ai_faction_tactical frequency
    # message : just a string (?)
    global channels
    # add the message to the channel
    radios=channels[frequency]
    for b in radios:
        b.ai.receive_message(message)


