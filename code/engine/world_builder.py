
'''
module : world_builder.py
language : Python 3.x
email : andrew@openmarmot.com
notes : 

static module with the following responsibilities
- build worlds
- load art assets (?)
- create world objects (can be called by anything)

the idea is this static class holds the standard way for creating objects
- anything that creates objects should do it here

# ref

'''


#import built in modules
from ai.ai_vehicle import AIVehicle
from ai.ai_human import AIHuman
import math
import random
import copy 
import os

#import custom packages
import engine.math_2d
import engine.name_gen

from engine.world_object import WorldObject
from engine.world_area import WorldArea


# load AI 
from ai.ai_human import AIHuman
from ai.ai_gun import AIGun
from ai.ai_magazine import AIMagazine
from ai.ai_none import AINone
from ai.ai_building import AIBuilding
from ai.ai_projectile import AIProjectile
from ai.ai_throwable import AIThrowable
from ai.ai_squad import AISquad
from ai.ai_map_pointer import AIMapPointer
from ai.ai_container import AIContainer
from ai.ai_consumable import AIConsumable
from ai.ai_medical import AIMedical
from ai.ai_engine import AIEngine
from ai.ai_coffee_grinder import AICoffeeGrinder
from ai.ai_animated_sprite import AIAnimatedSprite
from ai.ai_wearable import AIWearable
from ai.ai_battery import AIBattery
from ai.ai_radio import AIRadio
from ai.ai_turret import AITurret

#global variables

# ------ object rarity lists -----------------------------------
list_consumables=['green_apple','potato','turnip','cucumber','pickle','adler-cheese','camembert-cheese'
,'champignon-cheese','karwendel-cheese','wine','schokakola']
list_consumables_common=['green_apple','potato','turnip','cucumber','pickle']
list_consumables_rare=['adler-cheese','camembert-cheese','champignon-cheese','karwendel-cheese','wine','beer']
list_consumables_ultra_rare=['schokakola']

list_household_items=['blue_coffee_cup','coffee_tin','coffee_grinder','pickle_jar']

list_guns=['kar98k','stg44','mp40','mg34','mosin_nagant','ppsh43','dp28','1911','ppk','tt33','g41w','k43','svt40','svt40-sniper','mg15']
list_guns_common=['kar98k','mosin_nagant','ppsh43','tt33','svt40']
list_guns_rare=['mp40','ppk','stg44','mg34','dp28','k43','g41w']
list_guns_ultra_rare=['fg42-type1','fg42-type2','svt40-sniper','1911','mg15']
list_german_guns=['kar98k','stg44','mp40','mg34','ppk','k43','g41w','fg42-type1','fg42-type2']

list_german_military_equipment=['german_folding_shovel','german_field_shovel']

list_medical=['bandage','german_officer_first_aid_kit']
list_medical_common=['bandage']
list_medical_rare=['german_officer_first_aid_kit']
list_medical_ultra_rare=[]
#----------------------------------------------------------------

#------------------------------------------------------------------------------
def create_standard_squad(world,faction_tactial,world_coords,squad_type):
    ''' creates and spawns a standardized squad '''
    # radomize location a little so everything isn't on top of each other 
    world_coords=[world_coords[0]+float(random.randint(-200,200)),world_coords[1]+float(random.randint(-200,200))]

    s=AISquad(world)
    s.faction_tactical=faction_tactial
    s.destination=world_coords

    if squad_type=='soviet 1943 rifle':
        s.faction='soviet'
        # ref : https://www.battleorder.org/ussr-rifle-co-1943
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords)) # squad lead 
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords)) # asst squad lead could hav svt_40
        s.members.append(spawn_soldiers(world,'soviet_dp28',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
    elif squad_type=='soviet 1944 rifle':
        s.faction='soviet'
        # ref : https://www.battleorder.org/ussr-rifle-co-1944
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords)) # squad lead 
        s.members.append(spawn_soldiers(world,'soviet_svt40',world_coords)) # asst squad lead could hav svt_40
        s.members.append(spawn_soldiers(world,'soviet_dp28',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
    elif squad_type=='soviet 1944 rifle motorized':
        s.faction='soviet'
        # ref : https://www.battleorder.org/ussr-rifle-co-1944
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords)) # squad lead 
        s.members.append(spawn_soldiers(world,'soviet_svt40',world_coords)) # asst squad lead could hav svt_40
        s.members.append(spawn_soldiers(world,'soviet_dp28',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_mosin_nagant',world_coords))
        s.starting_vehicles.append(spawn_object(world,world_coords,'dodge_g505_wc',False))
    elif squad_type=='soviet 1944 submachine gun':
        s.faction='soviet'
        # ref : https://www.battleorder.org/ussr-rifle-co-1944
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords)) # squad lead 
        s.members.append(spawn_soldiers(world,'soviet_svt40',world_coords)) # asst squad lead could hav svt_40
        s.members.append(spawn_soldiers(world,'soviet_dp28',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords))
        s.members.append(spawn_soldiers(world,'soviet_ppsh43',world_coords))
    elif squad_type=='german 1944 rifle':
        s.faction='german'
        s.members.append(spawn_soldiers(world,'german_mp40',world_coords))
        s.members.append(spawn_soldiers(world,'german_mp40',world_coords))
        s.members.append(spawn_soldiers(world,'german_mg34',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'german_kar98k_panzerfaust',world_coords))
        s.members.append(spawn_soldiers(world,'german_kar98k_panzerfaust',world_coords))
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords))
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords))
        s.members.append(spawn_soldiers(world,'german_k43',world_coords))
    elif squad_type=='german 1944 panzergrenadier':
        s.faction='german'
        s.members.append(spawn_soldiers(world,'german_k43',world_coords))
        s.members.append(spawn_soldiers(world,'german_k43',world_coords))
        s.members.append(spawn_soldiers(world,'german_mg34',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'german_kar98k_panzerfaust',world_coords))
        s.members.append(spawn_soldiers(world,'german_kar98k_panzerfaust',world_coords))
        s.members.append(spawn_soldiers(world,'german_stg44_panzerfaust',world_coords))
        s.members.append(spawn_soldiers(world,'german_stg44_panzerfaust',world_coords))
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords))
        s.starting_vehicles.append(spawn_object(world,world_coords,'sd_kfz_251',False))
    elif squad_type=='german 1944 volksgrenadier fire group':
        s.faction='german'
        # ref : https://www.battleorder.org/volksgrenadiers-1944
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) #squad lead
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) # deputy squad lead
        s.members.append(spawn_soldiers(world,'german_mg34',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'german_mg34',world_coords)) # machine gunner
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) # asst machine gunner
        s.members.append(spawn_soldiers(world,'german_stg44_panzerfaust',world_coords)) # ammo bearer
        s.members.append(spawn_soldiers(world,'german_stg44_panzerfaust',world_coords)) # ammo bearer 
    elif squad_type=='german 1944 volksgrenadier storm group':
        s.faction='german'
        # ref : https://www.battleorder.org/volksgrenadiers-1944
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) #squad lead
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) # deputy squad lead
        s.members.append(spawn_soldiers(world,'german_stg44_panzerfaust',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_stg44_panzerfaust',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_stg44_panzerfaust',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_stg44',world_coords)) #  rifle man
    elif squad_type=='german 1944 fallschirmjager':
        s.faction='german'
        # ref : 
        s.members.append(spawn_soldiers(world,'german_fg42-type2',world_coords)) #squad lead
        s.members.append(spawn_soldiers(world,'german_fg42-type2',world_coords)) # deputy squad lead
        s.members.append(spawn_soldiers(world,'german_mg34',world_coords)) #  mg
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) #  asst mg
        s.members.append(spawn_soldiers(world,'german_kar98k_panzerfaust',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_kar98k_panzerfaust',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) #  rifle man
        s.members.append(spawn_soldiers(world,'german_kar98k',world_coords)) #  medic
    elif squad_type=='civilian small random':
        s.faction='civilian'
        amount=random.randint(1,3)
        for c in range(amount):
            s.members.append(spawn_civilians(world,'default',world_coords))
    elif squad_type=='big cheese':
        s.faction='civilian'
        s.members.append(spawn_civilians(world,'big_cheese',world_coords))
    elif squad_type=='shovel man':
        s.faction='civilian'
        s.members.append(spawn_civilians(world,'shovel_man',world_coords))
    else:
        print('!! Error : squad type not recognized : '+squad_type)

    # set the squad variable
    s.reset_squad_variable()

    # add to faction tactial
    faction_tactial.squads.append(s)
        
        
#------------------------------------------------------------------------------
def create_squads_from_human_list(world,HUMANS,FACTION):
    ''' takes a list of humans, sorts them by weapon type, and then puts them in squads'''

    # !! Note - this function is  not used at the moment and will probably need to be updated
    # to be used in the future
    print('warn! old function create_squads_from_human_list used')

    # automatically adds the created squads to the correct faction tactical AI
    assault_rifles=[]
    rifles=[]
    semiauto_rifles=[]
    subguns=[]
    machineguns=[]
    pistols=[]
    antitank=[]
    unidentified_human=[]
    unarmed_human=[]
    unarmed_vehicle=[]
    armed_vehicle=[]
    tank=[]
    airplane=[]

    # categorize 
    for b in HUMANS:
        if b.ai.primary_weapon==None:
            unarmed_human.append(b)
        elif b.ai.primary_weapon.name=='kar98k':
            rifles.append(b)
        elif b.ai.primary_weapon.name=='stg44':
            assault_rifles.append(b)
        elif b.ai.primary_weapon.name=='mp40':
            subguns.append(b)
        elif b.ai.primary_weapon.name=='mg34':
            machineguns.append(b)
        elif b.ai.primary_weapon.name=='mosin_nagant':
            rifles.append(b)
        elif b.ai.primary_weapon.name=='ppsh43':
            subguns.append(b)
        elif b.ai.primary_weapon.name=='dp28':
            machineguns.append(b)
        elif b.ai.primary_weapon.name=='1911':
            pistols.append(b)
        elif b.ai.primary_weapon.name=='ppk':
            pistols.append(b)
        elif b.ai.primary_weapon.name=='tt33':
            pistols.append(b)
        else:
            print('error: unknown primary weapon '+b.ai.primary_weapon.name+' in squad creation')

    squad_list=[]

    buildsquads=True 

    while buildsquads:
        if len(assault_rifles+rifles+semiauto_rifles+subguns+machineguns+antitank+pistols+unarmed_human)<1:
            buildsquads=False
        else :
            s=AISquad(world)
            s.faction=FACTION

            # -- build a rifle squad --
            if len(rifles)>7 :
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())
                s.members.append(rifles.pop())

                # mg ?
                if len(machineguns)>0:
                    s.members.append(machineguns.pop())

                # squad lead 
                if len(subguns)>0:
                    s.members.append(subguns.pop())
                elif len(assault_rifles)>0:
                    s.members.append(assault_rifles.pop())
                elif len(pistols)>0:
                    s.members.append(pistols.pop())
            # -- assault squad --
            elif len(assault_rifles)>4 :
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
                s.members.append(assault_rifles.pop())
            # -- erstaz groups --
            else :
                if len(rifles)>0:
                    s.members.append(rifles.pop())
                if len(semiauto_rifles)>0:
                    s.members.append(semiauto_rifles.pop())
                if len(subguns)>0:
                    s.members.append(subguns.pop())
                if len(assault_rifles)>0:
                    s.members.append(assault_rifles.pop())
                if len(machineguns)>0:
                    s.members.append(machineguns.pop())
                if len(antitank)>0:
                    s.members.append(antitank.pop())
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())
                if len(pistols)>0:
                    s.members.append(pistols.pop())
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())


                # lets do it again

                if len(rifles)>0:
                    s.members.append(rifles.pop())
                if len(semiauto_rifles)>0:
                    s.members.append(semiauto_rifles.pop())
                if len(subguns)>0:
                    s.members.append(subguns.pop())
                if len(assault_rifles)>0:
                    s.members.append(assault_rifles.pop())
                if len(machineguns)>0:
                    s.members.append(machineguns.pop())
                if len(antitank)>0:
                    s.members.append(antitank.pop())
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())
                if len(pistols)>0:
                    s.members.append(pistols.pop())
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())

                # and maybe one more time
                if len(rifles)>0:
                    s.members.append(rifles.pop())
                if len(semiauto_rifles)>0:
                    s.members.append(semiauto_rifles.pop())
                if len(subguns)>0:
                    s.members.append(subguns.pop())
                if len(assault_rifles)>0:
                    s.members.append(assault_rifles.pop())
                if len(machineguns)>0:
                    s.members.append(machineguns.pop())
                if len(antitank)>0:
                    s.members.append(antitank.pop())
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())
                if len(pistols)>0:
                    s.members.append(pistols.pop())
                if len(unarmed_human)>0:
                    s.members.append(unarmed_human.pop())               

            squad_list.append(s)

    return squad_list

#------------------------------------------------------------------------------
def fill_container(world,CONTAINER,FILL_NAME):
    ''' fill container with an object (liquid)'''
    # CONTAINER - should be empty
    # FILL_NAME - name of object (liquid) to fill the container with 

    fill=spawn_object(world,[0,0],FILL_NAME,False)
    fill.volume=CONTAINER.volume
    # need something more clever here.. maybe a density value per object
    fill.weight=CONTAINER.volume
    CONTAINER.ai.inventory.append(fill)


#------------------------------------------------------------------------------
def generate_clutter(world):
    '''generates and auto places small objects around the map'''
    # this should be called after buildings are placed

    # make sure anything pending is added/removed
    world.process_add_remove_queue()

    # building related clutter
    # need to smart position this in the future
    for b in world.wo_objects_building:
        chance=random.randint(0,15)
        coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
        coords2=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
        if chance==0 or chance==1:
            spawn_crate(world,coords,'random_consumables_common')
        elif chance==2:
            spawn_crate(world,coords,'random_consumables_rare')
        elif chance==3:
            spawn_crate(world,coords,'random_consumables_ultra_rare')
        elif chance==4:
            spawn_object(world,coords,'red_bicycle',True)
        elif chance==5 or chance==6:
            spawn_object(world,coords,'brown_chair',True)
        elif chance==7 or chance==8:
            spawn_object(world,coords,'cupboard',True)
        elif chance==9:
            spawn_aligned_pile(world,coords,coords2,'wood_log',6,5)
        elif chance==10:
            spawn_object(world,coords,'barrel',True)

    # supply drop 
    chance=random.randint(0,10)
    if chance==0:
        print('supply drop spawned')
        spawn_drop_canister(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'mixed_supply')

    # weapon crates 
    chance=random.randint(0,10)
    if chance==0:
        spawn_crate(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],"panzerfaust")
    if chance==1:
        spawn_crate(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],"random_one_gun_type")

    # kubelwagens
    chance=random.randint(0,10)
    if chance==0:
        k1=spawn_object(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'kubelwagen',True)
        k1=spawn_object(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'kubelwagen',True)

    # make sure there are a couple vehicles at least 
    if len(world.wo_objects_vehicle)<4:
        spawn_object(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'red_bicycle',True)
        spawn_object(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'red_bicycle',True)
        spawn_object(world,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'red_bicycle',True)

#------------------------------------------------------------------------------
def generate_civilians_and_civilan_spawns(world):
    '''generates civilans and civilan spawn points'''
    # this should be called after buildings are placed

    # make sure anything pending is added/removed
    world.process_add_remove_queue()

    for b in world.wo_objects_building:
        # add a random amount of civilians
        amount=random.randint(0,3)
        if amount>0:
            create_standard_squad(world,world.civilian_ai,b.world_coords,'civilian small random')

    # special case if there are no buildings
    if len(world.wo_objects_building)==0:
        print('WARN : No buildings')

    if random.randint(0,10)==10:
        print('big cheese!!')
        create_standard_squad(world,world.civilian_ai,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'big cheese')

#------------------------------------------------------------------------------
def generate_world_area(world,world_coords,TYPE,NAME):
    ''' generates the world areas on a NEW map. existing maps will pull this from the database '''
    # TYPE town, airport, bunkers, field_depot, train_depot 
    group=[]
    if TYPE=='town':
        count=random.randint(1,5)
        grid_spawn(world,world_coords,'warehouse',1150,count)
        count=random.randint(2,15)
        grid_spawn(world,world_coords,'square_building',250,count)
    elif TYPE=='fuel_dump':
        count=random.randint(11,157)
        grid_spawn(world,world_coords,'55_gallon_drum',20,count)
    elif TYPE=='german_ammo_dump':
        count=random.randint(11,45)
        grid_spawn(world,world_coords,'german_mg_ammo_can',30,count)
    elif TYPE=='german_fuel_can_dump':
        count=random.randint(21,75)
        grid_spawn(world,world_coords,'german_fuel_can',20,count)

    # make the corresponding WorldArea object
    w=WorldArea(world)
    w.world_coords=copy.copy(world_coords)
    w.name=NAME
    w.type=TYPE

    # register with world 
    world.world_areas.append(w)

#------------------------------------------------------------------------------
def get_random_from_list(world,world_coords,OBJECT_LIST,SPAWN):
    ''' returns a random object from a list'''
    # OBJECT_LIST : a list of strings that correspond to an object_Type for the 
    # spawn_object function
    index=random.randint(0,len(OBJECT_LIST)-1)
    return spawn_object(world,world_coords,OBJECT_LIST[index],SPAWN)

#------------------------------------------------------------------------------
def grid_spawn(world,world_coords,OBJECT_STRING,DIAMETER,COUNT):
    ''' spawn in a grid pattern '''
    last_coord=world_coords
    # this needs to be better
    column_max=engine.math_2d.get_optimal_column_count(COUNT)*DIAMETER

    for x in range(COUNT):
        
        if last_coord[0]>world_coords[0]+column_max:
            last_coord[0]=world_coords[0]
            last_coord[1]+=DIAMETER
        last_coord=[last_coord[0]+DIAMETER,last_coord[1]+0]
        spawn_object(world,last_coord,OBJECT_STRING,True)


#------------------------------------------------------------------------------
def load_magazine(world,magazine):
    '''loads a magazine with bullets'''
    count=len(magazine.ai.projectiles)
    while count<magazine.ai.capacity:
        z=spawn_object(world,[0,0],'projectile',False)
        z.ai.projectile_type=magazine.ai.compatible_projectiles[0]
        magazine.ai.projectiles.append(z)

        count+=1

#------------------------------------------------------------------------------
def load_test_environment(world,scenario):
    ''' test environment. not a normal map load '''


    if scenario=='1':
        # add some world areas
        generate_world_area(world,[-2000,2000],'town','Alfa')
        generate_world_area(world,[2000,-2000],'town','Bravo')
        generate_world_area(world,[2000,2000],'town','Charlie')
        generate_world_area(world,[float(random.randint(-3500,3500)),float(random.randint(-3500,3500))],'german_ammo_dump','german ammo dump')
        generate_world_area(world,[float(random.randint(-3500,3500)),float(random.randint(-3500,3500))],'german_fuel_can_dump','german fuel dump')

        # generate clutter after world areas are created
        generate_clutter(world)

        # generate civilians and civilan spawns
        generate_civilians_and_civilan_spawns(world)

        # some civilian reinforcements
        time=random.randint(120,800)
        world.reinforcements.append([time,'civilian',world.spawn_north,'civilian small random'])
        world.reinforcements.append([time,'civilian',world.spawn_north,'civilian small random'])

        # shovel man !
        if random.randint(0,10)==10:
            time=random.randint(120,500)
            world.reinforcements.append([time,'civilian',world.spawn_north,'shovel man'])


        # add germans
        create_standard_squad(world,world.german_ai,world.spawn_west,'german 1944 rifle')
        create_standard_squad(world,world.german_ai,world.spawn_west,'german 1944 rifle')
        create_standard_squad(world,world.german_ai,world.spawn_west,'german 1944 rifle')
        create_standard_squad(world,world.german_ai,world.spawn_west,'german 1944 volksgrenadier fire group')
        
        # add german reinforcements
        time=random.randint(120,500)
        world.reinforcements.append([time,'german',world.spawn_west,'german 1944 panzergrenadier'])
        world.reinforcements.append([time,'german',world.spawn_west,'german 1944 panzergrenadier'])

        # add soviets
        create_standard_squad(world,world.soviet_ai,world.spawn_far_east,'soviet 1944 rifle motorized')
        create_standard_squad(world,world.soviet_ai,world.spawn_far_east,'soviet 1944 rifle motorized')
        create_standard_squad(world,world.soviet_ai,world.spawn_far_east,'soviet 1944 rifle motorized')
        create_standard_squad(world,world.soviet_ai,world.spawn_far_east,'soviet 1944 rifle motorized')


        # add soviet reinforcements
        time=random.randint(120,500)
        world.reinforcements.append([time,'soviet',world.spawn_north,'soviet 1943 rifle'])
        time=random.randint(60,600)
        world.reinforcements.append([time,'soviet',world.spawn_south,'soviet 1943 rifle'])
        time=random.randint(120,700)
        world.reinforcements.append([time,'soviet',world.spawn_east,'soviet 1943 rifle'])

        # add ju88
        spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'ju88',True)

        # add a pile of bombs
        spawn_aligned_pile(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],[float(random.randint(-500,500)),float(random.randint(-500,500))],'bomb_sc250',15,4,False)

        # bikes 
        spawn_object(world,[float(random.randint(-1500,1500)),float(random.randint(-1500,1500))],'red_bicycle',True)

        # trucks 
        spawn_object(world,[float(random.randint(-1500,1500)),float(random.randint(-4500,4500))],'dodge_g505_wc',True)


  

#------------------------------------------------------------------------------
def spawn_aligned_pile(world,point_a,point_b,spawn_string,separation_distance,count,second_layer=True):
    ''' spawn an aligned pile like a wood pile'''
    # point_a - initial spawn point
    # point_b - direction in which the pile grows to 
    # spawn_string - name of the object to spawn
    # separation_distance - distance betwween objects

    rotation=engine.math_2d.get_rotation(point_a,point_b)
    heading=engine.math_2d.get_heading_from_rotation(rotation)
    

    # bottom layer
    current_coords=point_a
    for x in range(count):
        current_coords=engine.math_2d.moveAlongVector(separation_distance,current_coords,heading,1)

        x=spawn_object(world,point_a,spawn_string,True)
        x.rotation_angle=rotation
        x.heading=heading
        x.world_coords=current_coords

    if second_layer:
        current_coords=engine.math_2d.moveAlongVector(separation_distance/3,point_a,heading,1)
        for x in range(int(count/2)):
            current_coords=engine.math_2d.moveAlongVector(separation_distance,current_coords,heading,1)

            x=spawn_object(world,point_a,spawn_string,True)
            x.rotation_angle=rotation
            x.heading=heading
            x.world_coords=current_coords




#------------------------------------------------------------------------------
def spawn_civilians(world,CIVILIAN_TYPE,world_coords):
    ''' return a civilian with full kit '''
    # --------- german types ---------------------------------
    if CIVILIAN_TYPE=='default':
        z=spawn_object(world,world_coords,'civilian_man',True)
        z.world_builder_identity='civilian_default'
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
        return z
    elif CIVILIAN_TYPE=='pistol':
        z=spawn_object(world,world_coords,'civilian_man',True)
        z.world_builder_identity='civilian_default'
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.add_inventory(spawn_object(world,world_coords,'ppk',False))
        z.add_inventory(spawn_object(world,world_coords,'ppk_magazine',False))
        return z
    elif CIVILIAN_TYPE=='big_cheese':
        '''goofy unique civilain. don't mess with big cheese'''
        z=spawn_object(world,world_coords,'civilian_man',True)
        z.ai.health*=2
        z.name='big cheese'
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'adler-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'camembert-cheese',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust',False))
        return z
    elif CIVILIAN_TYPE=='shovel_man':
        '''goofy unique civilain. '''
        z=spawn_object(world,world_coords,'civilian_man',True)
        z.ai.health*=2
        z.name='Mr. Shovel'
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(world,world_coords,'coffee_tin',False))
        z.add_inventory(spawn_object(world,world_coords,'german_folding_shovel',False))
        z.add_inventory(spawn_object(world,world_coords,'german_field_shovel',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables_common,False))
        return z
#------------------------------------------------------------------------------
# currently used for wrecks and bodies
def spawn_container(name,world_object,image_index):
    '''spawns a custom container'''
    # name 
    # world_object - the world_object that is being replaced
    # image_index - index of the image to be used - from the world object
    z=WorldObject(world_object.world,[world_object.image_list[image_index]],AIContainer)
    z.is_container=True
    z.name=name
    z.world_coords=world_object.world_coords
    z.rotation_angle=world_object.rotation_angle
    z.ai.inventory=world_object.ai.inventory
    z.world_builder_identity='skip'
    z.volume=world_object.volume
    z.collision_radius=world_object.collision_radius
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_crate(world,world_coords,CRATE_TYPE):
    ''' generates different crate types with contents'''

    if CRATE_TYPE=='mp40':
        z=spawn_object(world,world_coords,'crate',True)
        z.ai.inventory.append(spawn_object(world,world_coords,'mp40',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'mp40',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'mp40',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'mp40',False))
    elif CRATE_TYPE=="random_consumables":
        z=spawn_object(world,world_coords,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables,False))
    elif CRATE_TYPE=="random_consumables_common":
        z=spawn_object(world,world_coords,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
    elif CRATE_TYPE=="random_consumables_rare":
        z=spawn_object(world,world_coords,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_rare,False))
    elif CRATE_TYPE=="random_consumables_ultra_rare":
        z=spawn_object(world,world_coords,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_ultra_rare,False))
    elif CRATE_TYPE=="random_guns":
        z=spawn_object(world,world_coords,'crate',True)
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_guns,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_guns,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_guns,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_guns,False))
    elif CRATE_TYPE=='panzerfaust':
        z=spawn_object(world,world_coords,'crate',True)
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
    elif CRATE_TYPE=='random_one_gun_type':
        z=spawn_object(world,world_coords,'crate',True)
        index=random.randint(0,len(list_guns)-1)
        amount= random.randint(1,6)
        for x in range(amount):
             z.ai.inventory.append(spawn_object(world,world_coords,list_guns[index],False))

#------------------------------------------------------------------------------
def spawn_drop_canister(world,world_coords,CRATE_TYPE):
    ''' generates different crate types with contents'''

    z=spawn_object(world,world_coords,'german_drop_canister',True)


    if CRATE_TYPE=='mixed_supply':
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_german_guns,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_german_guns,False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(world,world_coords,'panzerfaust',False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_medical,False))
        z.ai.inventory.append(get_random_from_list(world,world_coords,list_medical,False))

#------------------------------------------------------------------------------
def spawn_flash(world,world_coords,heading,amount=2):
    ''' spawn smoke cloud '''

    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_flash',True)
        z.heading=heading
        z.ai.speed=random.uniform(9,11)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(0.1,0.4)
  
#------------------------------------------------------------------------------
def spawn_object(world,world_coords,OBJECT_TYPE, SPAWN):
    '''returns new object. optionally spawns it in the world'''
    z=None
    if OBJECT_TYPE=='warehouse':
        z=WorldObject(world,['warehouse-outside','warehouse-inside'],AIBuilding)
        z.name='warehouse'
        z.collision_radius=200
        z.is_building=True

    elif OBJECT_TYPE=='square_building':
        z=WorldObject(world,['square_building_outside','square_building_inside'],AIBuilding)
        z.name='square building'
        z.collision_radius=60
        z.is_building=True

    elif OBJECT_TYPE=='green_apple':
        z=WorldObject(world,['green_apple'],AIConsumable)
        z.name='Green Apple'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-10 

    elif OBJECT_TYPE=='potato':
        z=WorldObject(world,['potato'],AIConsumable)
        z.name='potato'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-70
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-20  

    elif OBJECT_TYPE=='turnip':
        z=WorldObject(world,['turnip'],AIConsumable)
        z.name='turnip'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10  
    
    elif OBJECT_TYPE=='cucumber':
        z=WorldObject(world,['cucumber'],AIConsumable)
        z.name='cucumber'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10  

    elif OBJECT_TYPE=='pickle':
        z=WorldObject(world,['cucumber'],AIConsumable)
        z.name='pickle'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10 

    elif OBJECT_TYPE=='adler-cheese':
        z=WorldObject(world,['adler-cheese'],AIConsumable)
        z.name='Adler cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-200
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='camembert-cheese':
        z=WorldObject(world,['camembert-cheese'],AIConsumable)
        z.name='Camembert cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-250
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='champignon-cheese':
        z=WorldObject(world,['champignon-cheese'],AIConsumable)
        z.name='Champignon cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-300
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='karwendel-cheese':
        z=WorldObject(world,['karwendel-cheese'],AIConsumable)
        z.name='Karwendel cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-500
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='wine':
        z=WorldObject(world,['wine_bottle'],AIConsumable)
        z.name='wine'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-500
        z.ai.fatigue_effect=50

    elif OBJECT_TYPE=='beer':
        z=WorldObject(world,['green_bottle'],AIConsumable)
        z.name='beer'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-500
        z.ai.fatigue_effect=50   

    elif OBJECT_TYPE=='schokakola':
        z=WorldObject(world,['schokakola'],AIConsumable)
        z.name='scho-ka-kola'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=15
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=10
        z.ai.fatigue_effect=-250 
    elif OBJECT_TYPE=='bandage':
        z=WorldObject(world,['bandage'],AIMedical)
        z.name='bandage'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=50
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=0
    elif OBJECT_TYPE=='german_officer_first_aid_kit':
        z=WorldObject(world,['german_officer_first_aid_kit'],AIMedical)
        z.name='German Officer First Aid Kit'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=150
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=-300  

    elif OBJECT_TYPE=='german_fuel_can':
        z=WorldObject(world,['german_fuel_can'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.volume=20
        z.name='german_fuel_can'
        z.world_builder_identity='german_fuel_can'
        z.rotation_angle=float(random.randint(0,359))
        fill_container(world,z,'gas_80_octane')

    elif OBJECT_TYPE=='blue_coffee_cup':
        z=WorldObject(world,['blue_coffee_cup'],AIContainer)
        z.is_container=True
        z.volume=0.3
        z.name='blue_coffee_cup'
        z.world_builder_identity='blue_coffee_cup'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='55_gallon_drum':
        z=WorldObject(world,['55_gallon_drum'],AIContainer)
        z.is_container=True
        z.volume=208
        z.name='55_gallon_drum'
        z.collision_radius=15
        z.world_builder_identity='55_gallon_drum'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=208.2
        fill_container(world,z,'gas_80_octane')

    elif OBJECT_TYPE=='barrel':
        z=WorldObject(world,['barrel'],AIContainer)
        z.is_container=True
        z.volume=208
        z.name='barrel'
        z.collision_radius=15
        z.world_builder_identity='barrel'
        z.rotation_angle=float(random.randint(0,359))
        if random.randint(0,1)==1:
            fill_container(world,z,'water')

    elif OBJECT_TYPE=='german_mg_ammo_can':
        z=WorldObject(world,['german_mg_ammo_can'],AIContainer)
        z.is_ammo_container=True
        z.is_large_human_pickup=True
        z.name='german_mg_ammo_can'
        z.world_builder_identity='german_mg_ammo_can'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='german_drop_canister':
        z=WorldObject(world,['german_drop_canister'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='german drop canister'
        z.collision_radius=20
        z.world_builder_identity='german_drop_canister'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='crate':
        z=WorldObject(world,['crate'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='crate'
        z.collision_radius=20
        z.world_builder_identity='crate'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100

    elif OBJECT_TYPE=='small_crate':
        z=WorldObject(world,['small_crate'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='small_crate'
        z.collision_radius=20
        z.world_builder_identity='small_crate'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100

    elif OBJECT_TYPE=='cupboard':
        z=WorldObject(world,['cupboard'],AIContainer)
        z.is_container=True
        z.is_large_human_pickup=True
        z.name='cupboard'
        z.collision_radius=20
        z.world_builder_identity='cupboard'
        z.rotation_angle=float(random.randint(0,359))
        z.volume=100

        if random.randint(0,1)==1:
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_household_items,False))
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_household_items,False))
        if random.randint(0,1)==1:  
            z.ai.inventory.append(get_random_from_list(world,world_coords,list_consumables,False))


    elif OBJECT_TYPE=='coffee_tin':
        z=WorldObject(world,['coffee_tin'],AIContainer)
        z.is_container=True
        z.volume=1
        z.name='coffee_tin'
        z.world_builder_identity='coffee_tin'
        z.rotation_angle=float(random.randint(0,359))
        contents='coffee_beans'
        if random.randint(0,1)==1:
            contents='ground_coffee'
        fill_container(world,z,contents)

    elif OBJECT_TYPE=='jar':
        z=WorldObject(world,['jar'],AIContainer)
        z.is_container=True
        z.volume=1
        z.name='jar'
        z.world_builder_identity='jar'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='pickle_jar':
        z=spawn_object(world,world_coords,'jar',False)
        z.name='pickle jar'
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))
        z.add_inventory(spawn_object(world,world_coords,'pickle',False))

    elif OBJECT_TYPE=='panzerfaust':
        z=WorldObject(world,['panzerfaust','panzerfaust_empty'],AIGun)
        z.name='panzerfaust'
        z.ai.speed=300
        z.is_handheld_antitank=True
        z.ai.magazine=spawn_object(world,world_coords,'panzerfaust_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=0
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='antitank launcher'
        z.ai.smoke_on_fire=True
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='panzerfaust_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='panzerfaust_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['panzerfaust']
        z.ai.compatible_projectiles=['panzerfaust_60']
        z.ai.capacity=1
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        p=spawn_object(world,world_coords,'projectile',False)
        p.image_list=['panzerfaust_warhead']
        p.ai.projectile_type='panzerfaust_60'
        z.ai.projectiles.append(p)

    elif OBJECT_TYPE=='model24':
        z=WorldObject(world,['model24'],AIThrowable)
        z.name='model24'
        z.is_grenade=True
        z.is_throwable=True
        z.ai.explosive=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=3.0
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mp40':
        z=WorldObject(world,['mp40'],AIGun)
        z.name='mp40'
        z.world_builder_identity='gun_mp40'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mp40_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mp40_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mp40_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mp40']
        z.ai.compatible_projectiles=['9mm_124','9mm_115','9mm_ME']
        z.ai.capacity=32
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='ppsh43':
        z=WorldObject(world,['ppsh43'],AIGun)
        z.name='ppsh43'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'ppsh43_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ppsh43_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppsh43_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppsh43']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=35
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='stg44':
        z=WorldObject(world,['stg44'],AIGun)
        z.name='stg44'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'stg44_magazine',False)
        z.ai.rate_of_fire=0.1
        z.ai.reload_speed=7
        z.ai.flight_time=2.5
        z.ai.range=800
        z.ai.type='assault rifle'
        z.rotation_angle=float(random.randint(0,359))
    
    elif OBJECT_TYPE=='stg44_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='stg44_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['stg44']
        z.ai.compatible_projectiles=['7.92x33_SME']
        z.ai.capacity=30
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='dp28':
        z=WorldObject(world,['dp28'],AIGun)
        z.name='dp28'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'dp28_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=30
        z.ai.flight_time=3.5
        z.ai.range=800
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='dp28_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='dp28_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['dp28']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=47
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='ppk':
        z=WorldObject(world,['ppk'],AIGun)
        z.name='ppk'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'ppk_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.rotation_angle=float(random.randint(0,359))

    # NOTE - this should be 32 ACP or something
    elif OBJECT_TYPE=='ppk_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='ppk_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppk']
        z.ai.compatible_projectiles=['9mm_ME']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='tt33':
        z=WorldObject(world,['tt33'],AIGun)
        z.name='tt33'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'tt33_magazine',False)
        z.ai.rate_of_fire=0.9
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='tt33_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='tt33_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['tt33']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=8
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='1911':
        z=WorldObject(world,['1911'],AIGun)
        z.name='1911'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'1911_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.rotation_angle=float(random.randint(0,359))
    
    elif OBJECT_TYPE=='1911_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='1911_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['1911']
        z.ai.compatible_projectiles=['45acp']
        z.ai.capacity=7
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)


    elif OBJECT_TYPE=='mg34':
        z=WorldObject(world,['mg34'],AIGun)
        z.name='mg34'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mg34_drum_magazine',False)
        z.ai.rate_of_fire=0.05
        z.ai.reload_speed=13
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mg34_drum_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mg34_drum_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg34']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=50
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='mg15':
        z=WorldObject(world,['mg15'],AIGun)
        z.name='mg15'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mg15_drum_magazine',False)
        z.ai.rate_of_fire=0.06
        z.ai.reload_speed=13
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mg15_drum_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mg15_drum_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg15']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=75
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='kar98k':
        z=WorldObject(world,['kar98k'],AIGun)
        z.name='kar98k'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'kar98k_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=10
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='kar98k_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='kar98k_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['kar98k']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=5
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='g41w':
        z=WorldObject(world,['g41w'],AIGun)
        z.name='g41w'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'g41w_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='semi auto rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='g41w_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='g41w_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['g41w']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='k43':
        z=WorldObject(world,['k43'],AIGun)
        z.name='k43'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'k43_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='semi auto rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='k43_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='k43_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['k43']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='fg42-type1':
        z=WorldObject(world,['fg42-type1'],AIGun)
        z.name='fg42-type1'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'fg42_type1_magazine',False)
        z.ai.rate_of_fire=0.06
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='fg42_type1_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='fg42_type1_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type1']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='fg42-type2':
        z=WorldObject(world,['fg42-type2'],AIGun)
        z.name='fg42-type2'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'fg42_type2_magazine',False)
        z.ai.rate_of_fire=0.08
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='machine gun'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='fg42_type2_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='fg42_type2_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type2']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='mosin_nagant':
        z=WorldObject(world,['mosin_nagant'],AIGun)
        z.name='mosin_nagant'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'mosin_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=11
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mosin_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='mosin_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mosin_nagant']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=5
        z.ai.removable=False
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)
    
    elif OBJECT_TYPE=='svt40':
        z=WorldObject(world,['svt40'],AIGun)
        z.name='svt40'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'svt40_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='semi auto rifle'
        z.ai.projectile_type='7.62x54_L'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='svt40_magazine':
        z=WorldObject(world,['stg44_magazine'],AIMagazine)
        z.name='svt40_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['svt40','svt40-sniper']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=10
        z.ai.removable=True
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(world,z)

    elif OBJECT_TYPE=='svt40-sniper':
        z=WorldObject(world,['svt40-sniper'],AIGun)
        z.name='svt40-sniper'
        z.is_gun=True
        z.ai.magazine=spawn_object(world,world_coords,'svt40_magazine',False)
        z.ai.mag_capacity=10
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=8
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='semi auto rifle'
        z.ai.projectile_type='7.62x54_L'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='dodge_g505_wc':
        # ref : https://truck-encyclopedia.com/ww2/us/Dodge-WC-3-4-tons-series.php
        # ref : https://truck-encyclopedia.com/ww2/us/dodge-WC-62-63-6x6.php
        z=WorldObject(world,['dodge_g505_wc','dodge_g505_wc'],AIVehicle)
        z.name='Dodge G505 WC Truck'
        z.is_vehicle=True
        z.ai.max_occupants=10
        z.ai.max_speed=200
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=2380
        z.rolling_resistance=0.03
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"chrysler_flathead_straight_6_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='sd_kfz_251':
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_251','sd_kfz_251'],AIVehicle)
        z.name='Sd.Kfz.251'
        z.is_vehicle=True
        z.ai.armor_thickness=13
        z.ai.max_occupants=10
        z.ai.max_speed=200
        #z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=7800
        z.rolling_resistance=0.03
        z.drag_coefficient=0.9
        z.frontal_area=5
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=114
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"chrysler_flathead_straight_6_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[75,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))
        turret=spawn_object(world,world_coords,'sd_kfz_251_mg34_turret',True)
        z.ai.turrets.append(turret)
        turret.ai.vehicle=z
        # turret ammo, temporary 
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
        z.add_inventory(spawn_object(world,world_coords,'radio_feldfu_b',False))

        
    elif OBJECT_TYPE=='sd_kfz_251_mg34_turret':
        # !! note - turrets should be spawned with SPAWN TRUE as they are always in world
        # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
        z=WorldObject(world,['sd_kfz_251_mg34_turret','sd_kfz_251_mg34_turret'],AITurret)
        z.name='Sd.Kfz.251 MG34 Turret'
        z.is_turret=True
        z.ai.position_offset=[-10,0]
        z.ai.primary_weapon=spawn_object(world,world_coords,'mg34',False)
        z.ai.primary_weapon.ai.equipper=z
  
    elif OBJECT_TYPE=='kubelwagen':
        z=WorldObject(world,['kubelwagen','kubelwagen_destroyed'],AIVehicle)
        z.name='kubelwagen'
        z.is_vehicle=True
        z.ai.max_speed=200
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=800
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=3
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"volkswagen_type_82_engine",False))
        z.ai.engines[0].ai.exhaust_position_offset=[65,10]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_6v",False))
        if random.randint(0,3)==1:
            mg=spawn_object(world,world_coords,'mg34',False)
            z.add_inventory(mg)
            z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
            z.add_inventory(spawn_object(world,world_coords,"mg34_drum_magazine",False))
            z.add_inventory(spawn_object(world,world_coords,"german_mg_ammo_can",False))
            z.add_inventory(spawn_object(world,world_coords,"german_mg_ammo_can",False))
        z.add_inventory(spawn_object(world,world_coords,"german_fuel_can",False))
        z.add_inventory(get_random_from_list(world,world_coords,list_medical,False))
        z.add_inventory(get_random_from_list(world,world_coords,list_german_military_equipment,False))
        z.add_inventory(spawn_object(world,world_coords,'radio_feldfu_b',False))
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='red_bicycle':
        # note second image is used for the wreck..
        z=WorldObject(world,['red_bicycle','red_bicycle'],AIVehicle)
        z.name='red_bicycle'
        z.is_vehicle=True
        z.ai.max_speed=100
        z.ai.rotation_speed=50.
        z.ai.max_occupants=1
        z.ai.open_top=True
        z.collision_radius=50
        z.ai.engines.append(spawn_object(world,world_coords,"bicycle_pedals",False))
        z.weight=13
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=3

        if random.randint(0,3)==1:
            z.add_inventory(get_random_from_list(world,world_coords,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ju88':
        z=WorldObject(world,['ju88-winter-weathered','ju88-winter-weathered'],AIVehicle)
        z.name='Junkers Ju88'
        z.ai.max_speed=500
        z.ai.stall_speed=100
        z.ai.rotation_speed=50
        z.ai.acceleration=100
        z.ai.throttle_zero=False
        z.collision_radius=200
        mg=spawn_object(world,world_coords,'mg15',False)
        z.add_inventory(mg)
        z.ai.primary_weapon=mg
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg15_drum_magazine',False))
        z.is_airplane=True
        z.is_vehicle=True 
        z.rotation_angle=float(random.randint(0,359))
        z.weight=9800
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=6
        # fuel tank ref : https://airpages.ru/eng/lw/ju88_2.shtml
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks.append(spawn_object(world,world_coords,"vehicle_fuel_tank",False))
        z.ai.fuel_tanks[0].volume=415
        z.ai.fuel_tanks[1].volume=415
        z.ai.fuel_tanks[2].volume=425
        z.ai.fuel_tanks[3].volume=425
        fill_container(world,z.ai.fuel_tanks[0],'gas_80_octane')
        fill_container(world,z.ai.fuel_tanks[1],'gas_80_octane')
        fill_container(world,z.ai.fuel_tanks[2],'gas_80_octane')
        fill_container(world,z.ai.fuel_tanks[3],'gas_80_octane')
        z.ai.engines.append(spawn_object(world,world_coords,"jumo_211",False))
        z.ai.engines.append(spawn_object(world,world_coords,"jumo_211",False))
        z.ai.engines[0].ai.exhaust_position_offset=[-10,65]
        z.ai.engines[1].ai.exhaust_position_offset=[-10,-75]
        z.ai.batteries.append(spawn_object(world,world_coords,"battery_vehicle_24v",False))

    # this is only used briefly until the player picks a spawn type
    # this is required because a lot of stuff in the game references the player object.
    elif OBJECT_TYPE=='player':
        z=WorldObject(world,['man','civilian_prone','civilian_dead'],AIHuman)
        z.name='player'
        z.ai.speed=50.
        z.is_player=True
        z.is_human=True
        world.player=z

    elif OBJECT_TYPE=='civilian_man':
        z=WorldObject(world,['civilian_man','civilian_prone','civilian_dead'],AIHuman)
        z.name=engine.name_gen.get_name('civilian')
        z.ai.speed=float(random.randint(10,25))
        z.collision_radius=10
        z.is_human=True
        z.is_civilian=True

    elif OBJECT_TYPE=='german_soldier':
        z=WorldObject(world,['german_soldier','german_soldier_prone','german_dead'],AIHuman)
        z.name=engine.name_gen.get_name('german')
        z.ai.speed=float(random.randint(20,25))
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_german=True

    elif OBJECT_TYPE=='soviet_soldier':
        z=WorldObject(world,['soviet_soldier','soviet_soldier_prone','soviet_dead'],AIHuman)
        z.name=engine.name_gen.get_name('soviet')
        z.ai.speed=float(random.randint(20,25))
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_soviet=True

    elif OBJECT_TYPE=='brass':
        z=WorldObject(world,['brass'],AIAnimatedSprite)
        z.world_coords=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.name='brass'
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=150
        z.ai.rotation_speed=800
        z.ai.rotate_time_max=0.8
        z.ai.move_time_max=0.3
        z.ai.alive_time_max=1
        z.can_be_deleted=True  
    # steel bullet casing
    elif OBJECT_TYPE=='steel_case':
        z=WorldObject(world,['steel_case'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='steel_case'
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=150
        z.ai.rotation_speed=800
        z.ai.rotate_time_max=0.8
        z.ai.move_time_max=0.3
        z.ai.alive_time_max=1
        z.can_be_deleted=True
    elif OBJECT_TYPE=='small_smoke':
        z=WorldObject(world,['small_smoke'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_smoke'
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.can_be_deleted=True
    elif OBJECT_TYPE=='small_flash':
        z=WorldObject(world,['explosion_flash'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='small_flash'
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=15
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.can_be_deleted=True
    elif OBJECT_TYPE=='spark':
        z=WorldObject(world,['spark'],AIAnimatedSprite)
        w=[world_coords[0]+float(random.randint(-7,7)),world_coords[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.name='spark'
        z.is_particle_effect=True
        z.rotation_angle=float(random.randint(0,359))
        z.ai.speed=random.randint(100,300)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=3
        z.ai.self_remove=True
        z.can_be_deleted=True 
    
    elif OBJECT_TYPE=='blood_splatter':
        z=WorldObject(world,['blood_splatter'],AINone)
        z.name='blood_splatter'
        z.rotation_angle=float(random.randint(0,359))  

    elif OBJECT_TYPE=='small_blood':
        z=WorldObject(world,['small_blood'],AINone)
        z.name='small_blood'
        z.rotation_angle=float(random.randint(0,359)) 
           
    elif OBJECT_TYPE=='dirt':
        z=WorldObject(world,['small_dirt'],AINone)
        z.name='dirt'
        z.rotation_angle=float(random.randint(0,359))
        z.can_be_deleted=True
    
    elif OBJECT_TYPE=='brown_chair':
        z=WorldObject(world,['brown_chair'],AINone)
        z.name='brown_chair'
        z.is_furniture=True
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='german_field_shovel':
        z=WorldObject(world,['german_field_shovel'],AIThrowable)
        z.name='german field shovel'
        z.is_throwable=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=2
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='german_folding_shovel':
        z=WorldObject(world,['german_folding_shovel'],AIThrowable)
        z.name='german folding shovel'
        z.is_throwable=True
        z.ai.speed=112
        z.ai.max_speed=112
        z.ai.maxTime=2
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='volkswagen_type_82_engine':
        z=WorldObject(world,['volkswagen_type_82_engine'],AIEngine)
        z.name='Volkswagen Type 82 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=25277.9
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif OBJECT_TYPE=='chrysler_flathead_straight_6_engine':
        z=WorldObject(world,['volkswagen_type_82_engine'],AIEngine)
        z.name='Chrysler Flathead Straight 6 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=93022.91
        z.rotation_angle=float(random.randint(0,359))
        z.weight=250
    elif OBJECT_TYPE=='jumo_211':
        z=WorldObject(world,['jumo_211'],AIEngine)
        z.name='Jumo 211 Engine'
        z.ai.fuel_type=['gas_80_octane']
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=2549953.75 #based on 1000 hp
        z.rotation_angle=float(random.randint(0,359)) 
        z.weight=640
    elif OBJECT_TYPE=='vehicle_fuel_tank':
        z=WorldObject(world,['vehicle_fuel_tank'],AIContainer)
        z.is_container=True
        z.volume=20
        z.name='vehicle_fuel_tank'
        z.world_builder_identity='vehicle_fuel_tank'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='bicycle_pedals':
        z=WorldObject(world,['bicycle_pedals'],AIEngine)
        z.name='bicycle pedals'
        z.ai.internal_combustion=False
        z.ai.fuel_type='none'
        z.ai.fuel_consumption_rate=0
        z.ai.max_engine_force=131.44
        z.ai.engine_on=True
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='projectile':
        z=WorldObject(world,['projectile'],AIProjectile)
        z.name='projectile'
        z.ai.speed=350.
        z.is_projectile=True
    elif OBJECT_TYPE=='gas_80_octane':
        z=WorldObject(world,['small_clear_spill'],AIProjectile)
        z.name='gas_80_octane'
        z.is_liquid=True
        z.is_solid=False
    elif OBJECT_TYPE=='water':
        z=WorldObject(world,['small_clear_spill'],AIProjectile)
        z.name='water'
        z.is_liquid=True
        z.is_solid=False
    elif OBJECT_TYPE=='wood_log':
        z=WorldObject(world,['wood_log'],AINone)
        z.name='wood_log'
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='wood_quarter':
        z=WorldObject(world,['wood_log'],AINone)
        z.name='wood_log'
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='coffee_beans':
        z=WorldObject(world,['coffee_beans'],AINone)
        z.name='coffee_beans'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='ground_coffee':
        z=WorldObject(world,['coffee_beans'],AINone)
        z.name='ground_coffee'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='coffee_grinder':
        z=WorldObject(world,['coffee_grinder'],AICoffeeGrinder)
        z.name='coffee_grinder'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='bomb_sc250':
        z=WorldObject(world,['sc250'],AINone)
        z.name='bomb_sc250'
        z.weight=250
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='battery_feldfunk_2v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='Feldfunk 2V battery'
        z.weight=3
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='battery_vehicle_6v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='battery_vehicle_6v'
        z.weight=25
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='battery_vehicle_24v':
        z=WorldObject(world,['battery_vehicle_6v'],AIBattery)
        z.name='battery_vehicle_24v'
        z.weight=25
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='helmet_stahlhelm':
        z=WorldObject(world,['helmet_stahlhelm'],AIWearable)
        z.name='helmet_stahlhelm'
        z.weight=0.98
        z.is_wearable=True
        z.ai.wearable_region='head'
        z.ai.armor_thickness=3
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='helmet_ssh40':
        z=WorldObject(world,['helmet_ssh40'],AIWearable)
        z.name='helmet_ssh40'
        z.weight=0.98
        z.is_wearable=True
        z.ai.wearable_region='head'
        z.ai.armor_thickness=2
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='radio_feldfu_b':
        # ref https://feldfunker-la7sna.com/wehrm_foto.htm
        z=WorldObject(world,['radio_feldfunk'],AIRadio)
        z.name='Feldfunk.b'
        z.is_radio=True
        z.weight=15
        z.is_large_human_pickup=True
        z.ai.frequency_range=[90.57,109.45]
        z.ai.battery=spawn_object(world,world_coords,"battery_feldfunk_2v",False)
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='feldfunk_battery_charger':
        # ref https://feldfunker-la7sna.com/wehrm_foto.htm
        z=WorldObject(world,['radio_feldfunk_charger'],AIRadio)
        z.name='Feldfunk battery charger'
        z.weight=15
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359)) 

    else:
        print('!! Spawn Error: '+OBJECT_TYPE+' is not recognized.')  

    # -- generic settings that apply to all --
    z.world_builder_identity=OBJECT_TYPE
    # set world coords if they weren't already set
    if z.world_coords==[0,0]:
        z.world_coords=copy.copy(world_coords)

    # reset render level now that variables are set
    z.reset_render_level()
    if SPAWN :
        z.wo_start()
    return z


#------------------------------------------------------------------------------
def spawn_map_pointer(world,TARGET_COORDS,TYPE):
    if TYPE=='normal':
        z=WorldObject(world,['map_pointer_green'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()
    if TYPE=='blue':
        z=WorldObject(world,['map_pointer_blue'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()
    if TYPE=='orange':
        z=WorldObject(world,['map_pointer_orange'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()



#------------------------------------------------------------------------------
# basically just a different kind of projectile
def spawn_shrapnel(world,world_coords,TARGET_COORDS,IGNORE_LIST,PROJECTILE_TYPE,MIN_TIME,MAX_TIME,ORIGINATOR,WEAPON_NAME):
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(world,['shrapnel'],AIProjectile)
    z.name='shrapnel'
    z.world_coords=copy.copy(world_coords)
    z.ai.starting_coords=copy.copy(world_coords)
    z.ai.speed=300.
    z.ai.maxTime=random.uniform(MIN_TIME, MAX_TIME)
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=copy.copy(IGNORE_LIST)
    z.ai.projectile_type=PROJECTILE_TYPE
    z.rotation_angle=engine.math_2d.get_rotation(world_coords,TARGET_COORDS)
    z.heading=engine.math_2d.get_heading_vector(world_coords,TARGET_COORDS)
    # increase the collision radius to make sure we get hits
    z.collision_radius=10
    z.ai.shooter=ORIGINATOR
    z.ai.weapon_name=WEAPON_NAME
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_shrapnel_cloud(world,world_coords,AMOUNT,ORIGINATOR,WEAPON_NAME):
    ''' creates a shrapnel starburst pattern. used for grenades '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    ignore_list=[]
    if world.friendly_fire_explosive==False:
        if ORIGINATOR.is_german:
                ignore_list+=world.wo_objects_german
        elif ORIGINATOR.is_soviet:
            ignore_list+=world.wo_objects_soviet
        elif ORIGINATOR.is_american:
            ignore_list+=world.wo_objects_american
    elif world.friendly_fire_explosive_squad==False:
        # just add the squad
        ignore_list+=ORIGINATOR.ai.squad.members

    for x in range(AMOUNT):
        target_coords=[float(random.randint(-150,150))+world_coords[0],float(random.randint(-150,150))+world_coords[1]]
        spawn_shrapnel(world,world_coords,target_coords,ignore_list,'shrapnel',0.1,0.4,ORIGINATOR,WEAPON_NAME)

#------------------------------------------------------------------------------
def spawn_smoke_cloud(world,world_coords,heading,amount=30):
    ''' spawn smoke cloud '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel


    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'small_smoke',True)
        z.heading=heading
        z.ai.speed=random.uniform(9,11)
        z.ai.rotation_speed=random.randint(400,500)
        z.ai.rotate_time_max=1.8
        z.ai.move_time_max=3
        z.ai.alive_time_max=random.uniform(1.5,3)

#------------------------------------------------------------------------------
def spawn_sparks(world,world_coords,amount=30):
    ''' spawn spark '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel


    for x in range(amount):
        coords=[world_coords[0]+random.randint(-2,2),world_coords[1]+random.randint(-2,2)]
        z=spawn_object(world,coords,'spark',True)
        z.heading=engine.math_2d.get_heading_from_rotation(z.rotation_angle)
        z.ai.speed=random.uniform(60,70)
        z.ai.rotation_speed=0
        z.ai.rotate_time_max=0
        z.ai.move_time_max=1
        z.ai.alive_time_max=random.uniform(1.5,2)

#------------------------------------------------------------------------------
def spawn_heat_jet(world,world_coords,TARGET_COORDS,AMOUNT,ORIGINATOR,WEAPON_NAME):
    ''' creates a cone/line of shrapnel. used for panzerfaust'''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    for x in range(AMOUNT):
        target_coords=[float(random.randint(-5,5))+TARGET_COORDS[0],float(random.randint(-5,5))+TARGET_COORDS[1]]
        spawn_shrapnel(world,world_coords,target_coords,[],'HEAT_jet',0.1,0.3,ORIGINATOR,WEAPON_NAME)


#------------------------------------------------------------------------------
def spawn_soldiers(world,SOLDIER_TYPE,world_coords):
    ''' return a soldier with full kit '''
    # --------- german types ---------------------------------
    if SOLDIER_TYPE=='german_kar98k':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_kar98k'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        return z
    if SOLDIER_TYPE=='german_kar98k_panzerfaust':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_kar98k'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'kar98k_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust',False))
        return z
    if SOLDIER_TYPE=='german_k43':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_k43'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'k43',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'k43_magazine',False))
        return z
    if SOLDIER_TYPE=='german_g41w':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_g41w'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'g41w_magazine',False))
        return z
    if SOLDIER_TYPE=='german_mp40':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_mp40'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mp40_magazine',False))
        return z
    if SOLDIER_TYPE=='german_mg34':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_mg34'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mg34_drum_magazine',False))
        return z
    if SOLDIER_TYPE=='german_stg44':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_stg44'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        return z
    if SOLDIER_TYPE=='german_stg44_panzerfaust':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_stg44'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'stg44_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'panzerfaust',False))
        return z
    if SOLDIER_TYPE=='german_fg42-type2':
        z=spawn_object(world,world_coords,'german_soldier',True)
        z.world_builder_identity='german_fg42-type2'
        z.add_inventory(spawn_object(world,world_coords,'helmet_stahlhelm',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42-type2',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'fg42_type2_magazine',False))
        return z

    # --------- soviet types ----------------------------------------
    if SOLDIER_TYPE=='soviet_mosin_nagant':
        z=spawn_object(world,world_coords,'soviet_soldier',True)
        z.world_builder_identity='soviet_mosin_nagant'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_nagant',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'mosin_magazine',False))
        return z
    if SOLDIER_TYPE=='soviet_svt40':
        z=spawn_object(world,world_coords,'soviet_soldier',True)
        z.world_builder_identity='soviet_svt40'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'svt40_magazine',False))
        return z
    if SOLDIER_TYPE=='soviet_ppsh43':
        z=spawn_object(world,world_coords,'soviet_soldier',True)
        z.world_builder_identity='soviet_ppsh43'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'ppsh43_magazine',False))
        return z 
    if SOLDIER_TYPE=='soviet_dp28':
        z=spawn_object(world,world_coords,'soviet_soldier',True)
        z.world_builder_identity='soviet_dp28'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'dp28_magazine',False))
        return z 
    if SOLDIER_TYPE=='soviet_tt33':
        z=spawn_object(world,world_coords,'soviet_soldier',True)
        z.world_builder_identity='soviet_tt33'
        z.add_inventory(spawn_object(world,world_coords,'helmet_ssh40',False))
        z.add_inventory(spawn_object(world,world_coords,'tt33',False))
        z.add_inventory(spawn_object(world,world_coords,'model24',False))
        z.add_inventory(spawn_object(world,world_coords,'bandage',False))
        z.add_inventory(spawn_object(world,world_coords,'tt33_magazine',False))
        z.add_inventory(spawn_object(world,world_coords,'tt33_magazine',False)) 
        return z   
