'''
module : engine/penetration_calculator.py
language : Python 3.x
email : andrew@openmarmot.com
notes : various penetration "calculations"
'''


#import built in modules
import random
#import custom packages
import engine.math_2d



# velocity is in feet per second
# note velocity doesn't make sense here - it should be per weapon per projectile type

projectile_data={}
projectile_data['9mm_124']={'material':'lead','case_material':'brass','grain_weight':124,'velocity':1050,'contact_effect':'none','shrapnel_count':0,'notes':'standard german early war fmj 9mm'}
projectile_data['9mm_115']={'material':'lead','case_material':'brass','grain_weight':115,'velocity':1200,'contact_effect':'none','shrapnel_count':0,'notes':'standard us/commonwealth fmj 9mm'}
projectile_data['9mm_ME']={'material':'mild_steel','case_material':'steel','grain_weight':94,'velocity':1500,'contact_effect':'none','shrapnel_count':0,'notes':'standard german issue late war iron core'}
projectile_data['45acp']={'material':'lead','case_material':'steel','grain_weight':230,'velocity':800,'contact_effect':'none','shrapnel_count':0,'notes':'standard issue 45 ACP'}
projectile_data['7.62x25']={'material':'lead','case_material':'steel','grain_weight':90,'velocity':1450,'contact_effect':'none','shrapnel_count':0,'notes':'standard tokarev ammo, probably light ap'}
projectile_data['7.62x54_L']={'material':'lead','case_material':'steel','grain_weight':147,'velocity':2838,'contact_effect':'none','shrapnel_count':0,'notes':'standard soviet light ball'}
projectile_data['7.62x54_D']={'material':'mild_steel','case_material':'steel','grain_weight':185,'velocity':2600,'contact_effect':'none','shrapnel_count':0,'notes':'heavy ball, light ap'}
projectile_data['7.92x57_SSP']={'material':'lead','case_material':'brass','grain_weight':197.53,'velocity':2493,'contact_effect':'none','shrapnel_count':0,'notes':'german early war/sniper ss patrone '}
projectile_data['7.92x57_SME']={'material':'mild_steel','case_material':'steel','grain_weight':178.2,'velocity':2592,'contact_effect':'none','shrapnel_count':0,'notes':'standard issue german iron core '}
projectile_data['7.92x57_SMK']={'material':'hard_steel','case_material':'steel','grain_weight':182.9,'velocity':2575,'contact_effect':'none','shrapnel_count':0,'notes':'german standard ap '}
projectile_data['7.92x57_SMKH']={'material':'tungsten','case_material':'steel','grain_weight':178.2,'velocity':2592,'contact_effect':'none','shrapnel_count':0,'notes':'extra hard ap '}
projectile_data['7.92x33_SME']={'material':'mild_steel','case_material':'steel','grain_weight':125,'velocity':2250,'contact_effect':'none','shrapnel_count':0,'notes':'standard issue german iron core for stg44 '}
projectile_data['panzerfaust_60']={'material':'copper','case_material':'cardboard','grain_weight':150,'velocity':800,'contact_effect':'HEAT','shrapnel_count':30,'notes':'super-plastic metal jet from heat warhead '}

# second order projectiles
projectile_data['shrapnel']={'material':'mild_steel','case_material':'none','grain_weight':50,'velocity':1100,'contact_effect':'none','shrapnel_count':0,'notes':'fragment from a grenade '}
projectile_data['HEAT_jet']={'material':'copper','case_material':'none','grain_weight':150,'velocity':22000,'contact_effect':'none','shrapnel_count':0,'notes':'super-plastic metal jet from heat warhead '}




#---------------------------------------------------------------------------
def check_passthrough(PROJECTILE,TARGET):
    ''' returns bool as to whether or not a projectile passed through (over pen) an object '''
    # PROJECTILE - world_object representing the projectile
    # TARGET - world_object that is hit by the projectile

    passthrough=False
    if TARGET.is_building:
        passthrough=get_building_passthrough(PROJECTILE,TARGET)
    elif TARGET.is_human:
        passthrough=get_human_passthrough(PROJECTILE,TARGET)
    elif TARGET.is_vehicle:
        passthrough=True

    return passthrough

#---------------------------------------------------------------------------
def get_building_passthrough(PROJECTILE,TARGET):
    proj_material=projectile_data[PROJECTILE.ai.projectile_type]['material']
    passthrough=False
    if proj_material=='mild_steel':
        if random.randint(1,100) <40:
            passthrough=True
    elif proj_material=='hard_steel':
        if random.randint(1,100) <60:
            passthrough=True
    elif proj_material=='tungsten':
        if random.randint(1,100) <80:
            passthrough=True
    else :
        # everything else - mostly lead
        if random.randint(1,100) <20:
            passthrough=True
    return passthrough

#---------------------------------------------------------------------------
def get_human_passthrough(PROJECTILE,TARGET):
    proj_material=projectile_data[PROJECTILE.ai.projectile_type]['material']
    passthrough=False
    if proj_material=='mild_steel':
        if random.randint(1,100) <50:
            passthrough=True
    elif proj_material=='hard_steel':
        if random.randint(1,100) <80:
            passthrough=True
    elif proj_material=='tungsten':
        if random.randint(1,100) <90:
            passthrough=True
    else :
        # everything else - mostly lead
        if random.randint(1,100) <20:
            passthrough=True
    return passthrough

#---------------------------------------------------------------------------
def get_vehicle_passthrough(PROJECTILE,TARGET):

    # eventually vehicles will get a unique penetration calculation to check armor 

    proj_material=projectile_data[PROJECTILE.ai.projectile_type]['material']
    passthrough=False
    if proj_material=='mild_steel':
        if random.randint(1,100) <50:
            passthrough=True
    elif proj_material=='hard_steel':
        if random.randint(1,100) <80:
            passthrough=True
    elif proj_material=='tungsten':
        if random.randint(1,100) <90:
            passthrough=True
    else :
        # everything else - mostly lead
        if random.randint(1,100) <20:
            passthrough=True
    return passthrough
            