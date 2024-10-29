'''
module : engine/world_radio.py
language : Python 3.x
email : andrew@openmarmot.com
notes : handles the radio simulation
'''

import engine.log

# this gets wiped on world.init to prevent stale objects from previous worlds
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
        channels[frequency]=[radio]
        engine.log.add_data('note','world_radio.add_radio frequency channel '+str(frequency)+' does not exist. creating..',True)

#---------------------------------------------------------------------------
def remove_radio(radio):
    '''remove a radio from all channels'''
    # this is called by ai_radio
    global channels
    for r in channels.values():
        if radio in r:
            r.remove(radio)

#---------------------------------------------------------------------------
def reset_world_radio():
    '''reset to defaults'''
    # used when doing world.init so there are no old radio references
    global channels
    channels={}

#---------------------------------------------------------------------------
def send_message(frequency,message):
    # frequency : should match a ai_faction_tactical frequency
    # message : just a string (?)
    global channels
    # add the message to the channel
    radios=channels[frequency]
    for b in radios:
        b.ai.receive_message(message)


