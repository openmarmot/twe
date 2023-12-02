
'''
module : world_builder.py
version : see module_version variable
Language : Python 3.x
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

#import custom packages
from engine.world import World
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
from ai.ai_liquid_container import AILiquidContainer
from ai.ai_consumable import AIConsumable
from ai.ai_medical import AIMedical
from ai.ai_engine import AIEngine


#global variables

# ------ object rarity lists -----------------------------------
list_consumables=['green_apple','potato','turnip','adler-cheese','camembert-cheese'
,'champignon-cheese','karwendel-cheese','wine','schokakola']
list_consumables_common=['green_apple','potato','turnip']
list_consumables_rare=['adler-cheese','camembert-cheese','champignon-cheese','karwendel-cheese','wine']
list_consumables_ultra_rare=['schokakola']

list_guns=['kar98k','stg44','mp40','mg34','mosin_nagant','ppsh43','dp28','1911','ppk','tt33','g41w','k43','svt40','svt40-sniper']
list_guns_common=['kar98k','mosin_nagant','ppsh43','tt33','svt40']
list_guns_rare=['mp40','ppk','stg44','mg34','dp28','1911','k43','g41w']
list_guns_ultra_rare=['fg42-type1','fg42-type2','svt40-sniper']
list_german_guns=['kar98k','stg44','mp40','mg34','ppk','k43','g41w','fg42-type1','fg42-type2']

list_german_military_equipment=['german_folding_shovel','german_field_shovel']

list_medical=['bandage','german_officer_first_aid_kit']
list_medical_common=['bandage']
list_medical_rare=['german_officer_first_aid_kit']
list_medical_ultra_rare=[]
#----------------------------------------------------------------

#------------------------------------------------------------------------------
def add_standard_squad(WORLD,SQUAD_TYPE):
    ''' adds a standardized squad to a factions spawn queue '''
    s=AISquad(WORLD)
    if SQUAD_TYPE=='soviet 1943 rifle':
        s.faction='soviet'
        # ref : https://www.battleorder.org/ussr-rifle-co-1943
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43')) # squad lead 
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant')) # asst squad lead could hav svt_40
        s.members.append(spawn_soldiers(WORLD,'soviet_dp28')) # machine gunner
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant')) # asst machine gunner
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        WORLD.soviet_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='soviet 1944 rifle':
        s.faction='soviet'
        # ref : https://www.battleorder.org/ussr-rifle-co-1944
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43')) # squad lead 
        s.members.append(spawn_soldiers(WORLD,'soviet_svt40')) # asst squad lead could hav svt_40
        s.members.append(spawn_soldiers(WORLD,'soviet_dp28')) # machine gunner
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43')) # asst machine gunner
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        s.members.append(spawn_soldiers(WORLD,'soviet_mosin_nagant'))
        WORLD.soviet_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='soviet 1944 submachine gun':
        s.faction='soviet'
        # ref : https://www.battleorder.org/ussr-rifle-co-1944
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43')) # squad lead 
        s.members.append(spawn_soldiers(WORLD,'soviet_svt40')) # asst squad lead could hav svt_40
        s.members.append(spawn_soldiers(WORLD,'soviet_dp28')) # machine gunner
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43')) # asst machine gunner
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43'))
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43'))
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43'))
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43'))
        s.members.append(spawn_soldiers(WORLD,'soviet_ppsh43'))
        WORLD.soviet_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='german 1944 rifle':
        s.faction='german'
        s.members.append(spawn_soldiers(WORLD,'german_mp40'))
        s.members.append(spawn_soldiers(WORLD,'german_mp40'))
        s.members.append(spawn_soldiers(WORLD,'german_mg34')) # machine gunner
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) # asst machine gunner
        s.members.append(spawn_soldiers(WORLD,'german_kar98k'))
        s.members.append(spawn_soldiers(WORLD,'german_kar98k'))
        s.members.append(spawn_soldiers(WORLD,'german_kar98k'))
        s.members.append(spawn_soldiers(WORLD,'german_kar98k'))
        s.members.append(spawn_soldiers(WORLD,'german_kar98k'))
        WORLD.german_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='german 1944 volksgrenadier fire group':
        s.faction='german'
        # ref : https://www.battleorder.org/volksgrenadiers-1944
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #squad lead
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) # deputy squad lead
        s.members.append(spawn_soldiers(WORLD,'german_mg34')) # machine gunner
        s.members.append(spawn_soldiers(WORLD,'german_mg34')) # machine gunner
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) # asst machine gunner
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) # asst machine gunner
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) # ammo bearer
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) # ammo bearer 
        WORLD.german_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='german 1944 volksgrenadier storm group':
        s.faction='german'
        # ref : https://www.battleorder.org/volksgrenadiers-1944
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #squad lead
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) # deputy squad lead
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_stg44')) #  rifle man
        WORLD.german_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='german 1944 fallschirmjager':
        s.faction='german'
        # ref : 
        s.members.append(spawn_soldiers(WORLD,'german_fg42-type2')) #squad lead
        s.members.append(spawn_soldiers(WORLD,'german_fg42-type2')) # deputy squad lead
        s.members.append(spawn_soldiers(WORLD,'german_mg34')) #  mg
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  asst mg
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  rifle man
        s.members.append(spawn_soldiers(WORLD,'german_kar98k')) #  medic
        WORLD.german_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='civilian small random':
        s.faction='civilian'
        amount=random.randint(1,3)
        for c in range(amount):
            s.members.append(spawn_civilians(WORLD,'default'))
        WORLD.civilian_ai.squad_spawn_queue.append(s)
    elif SQUAD_TYPE=='big cheese':
        s.faction='civilian'
        s.members.append(spawn_civilians(WORLD,'big cheese'))
        WORLD.civilian_ai.squad_spawn_queue.append(s)
    else:
        print('!! Error : squad type not recognized : '+SQUAD_TYPE)
        
        

#------------------------------------------------------------------------------
def create_squads_from_human_list(WORLD,HUMANS,FACTION):
    ''' takes a list of humans, sorts them by weapon type, and then puts them in squads'''

    # note - i think this isn't used anymore - but its a good bit of code so will keep for future use

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
            s=AISquad(WORLD)
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

    if FACTION=='civilian':
        WORLD.civilian_ai.squad_spawn_queue+=squad_list
    elif FACTION=='german':
        WORLD.german_ai.squad_spawn_queue+=squad_list
    elif FACTION=='soviet':
        WORLD.soviet_ai.squad_spawn_queue+=squad_list
    elif FACTION=='american':
        WORLD.american_ai.squad_spawn_queue+=squad_list
    else:
        print('ERROR ! : Faction not recognized in world_builder.create_squad()')
            

#------------------------------------------------------------------------------
def generate_clutter(WORLD):
    '''generates and auto places small objects around the map'''
    # this should be called after buildings are placed

    # building related clutter
    # need to smart position this in the future
    for b in WORLD.wo_objects_building:
        chance=random.randint(0,8)
        coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
        if chance==0 or chance==1:
            spawn_crate(WORLD,coords,'random_consumables_common')
        elif chance==2:
            spawn_crate(WORLD,coords,'random_consumables_rare')
        elif chance==3:
            spawn_crate(WORLD,coords,'random_consumables_ultra_rare')
        elif chance==4:
            spawn_object(WORLD,coords,'red_bicycle',True)
        elif chance==5 or chance==6 or chance==7:
            spawn_object(WORLD,coords,'brown_chair',True)

    # supply drop 
    chance=random.randint(0,10)
    if chance==0:
        print('supply drop spawned')
        spawn_drop_canister(WORLD,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'mixed_supply')

    # weapon crates 
    chance=random.randint(0,10)
    if chance==0:
        spawn_crate(WORLD,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],"panzerfaust")
    if chance==1:
        spawn_crate(WORLD,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],"random_one_gun_type")

    # kubelwagens
    chance=random.randint(0,10)
    if chance==0:
        k1=spawn_object(WORLD,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'kubelwagen',True)
        k1.ai.fuel_tanks[0].ai.used_volume=random.randint(0,k1.ai.fuel_tanks[0].ai.total_volume)
        k1=spawn_object(WORLD,[float(random.randint(-2500,2500)),float(random.randint(-2500,2500))],'kubelwagen',True)
        k1.ai.fuel_tanks[0].ai.used_volume=random.randint(0,k1.ai.fuel_tanks[0].ai.total_volume)


#------------------------------------------------------------------------------
def generate_civilians_and_civilan_spawns(WORLD):
    '''generates civilans and civilan spawn points'''
    # this should be called after buildings are placed

    for b in WORLD.wo_objects_building:
        # add a random amount of civilians
        amount=random.randint(0,3)
        if amount>0:
            add_standard_squad(WORLD,'civilian small random')

        # add the spawn point
        WORLD.civilian_ai.spawn_points.append(b.world_coords)

    # special case if there are no buildings
    if len(WORLD.wo_objects_building)==0:
        print('WARN : No buildings, default civilian spawn added')
        WORLD.civilian_ai.spawn_points.append([0,0])

    if random.randint(0,10)==10:
        print('big cheese!!')
        add_standard_squad(WORLD,'big cheese')


#------------------------------------------------------------------------------
def generate_world_area(WORLD,WORLD_COORDS,TYPE,NAME):
    ''' generates the world areas on a NEW map. existing maps will pull this from the database '''
    # TYPE town, airport, bunkers, field_depot, train_depot 
    group=[]
    if TYPE=='town':
        count=random.randint(1,5)
        grid_spawn(WORLD,WORLD_COORDS,'warehouse',1150,count)
        count=random.randint(2,15)
        grid_spawn(WORLD,WORLD_COORDS,'square_building',250,count)
    elif TYPE=='fuel_dump':
        count=random.randint(11,157)
        grid_spawn(WORLD,WORLD_COORDS,'55_gallon_drum',20,count)
    elif TYPE=='german_ammo_dump':
        count=random.randint(11,45)
        grid_spawn(WORLD,WORLD_COORDS,'german_mg_ammo_can',30,count)
    elif TYPE=='german_fuel_can_dump':
        count=random.randint(21,75)
        grid_spawn(WORLD,WORLD_COORDS,'german_fuel_can',20,count)

    # make the corresponding worldArea object
    w=WorldArea(WORLD)
    w.world_coords=copy.copy(WORLD_COORDS)
    w.name=NAME
    w.type=TYPE

    # register with world 
    WORLD.world_areas.append(w)

#------------------------------------------------------------------------------
def get_random_from_list(WORLD,WORLD_COORDS,OBJECT_LIST,SPAWN):
    ''' returns a random object from a list'''
    # OBJECT_LIST : a list of strings that correspond to an object_Type for the 
    # spawn_object function
    index=random.randint(0,len(OBJECT_LIST)-1)
    return spawn_object(WORLD,WORLD_COORDS,OBJECT_LIST[index],SPAWN)

#------------------------------------------------------------------------------
def grid_spawn(WORLD,WORLD_COORDS,OBJECT_STRING,DIAMETER,COUNT):
    ''' spawn in a grid pattern '''
    last_coord=WORLD_COORDS
    # this needs to be better
    column_max=engine.math_2d.get_optimal_column_count(COUNT)*DIAMETER

    for x in range(COUNT):
        
        if last_coord[0]>WORLD_COORDS[0]+column_max:
            last_coord[0]=WORLD_COORDS[0]
            last_coord[1]+=DIAMETER
        last_coord=[last_coord[0]+DIAMETER,last_coord[1]+0]
        spawn_object(WORLD,last_coord,OBJECT_STRING,True)

#------------------------------------------------------------------------------
def initialize_world(SCREEN_SIZE):
    '''
    returns a world object that has completed basic init
    '''

    world = World(SCREEN_SIZE)

    load_images(world)

    return world

#------------------------------------------------------------------------------
def load_images(world):
    '''
    load art assets
    '''
    # people
    world.graphic_engine.loadImage('man','images/humans/man.png')
    world.graphic_engine.loadImage('german_soldier','images/humans/german_soldier.png')
    world.graphic_engine.loadImage('german_soldier_prone','images/humans/german_soldier_prone.png')
    world.graphic_engine.loadImage('german_dead','images/humans/german_dead.png')

    world.graphic_engine.loadImage('german_ss_fall_helm_soldier','images/humans/german_ss_fall_helm_soldier.png')
    
    world.graphic_engine.loadImage('soviet_soldier','images/humans/russian_soldier.png')
    world.graphic_engine.loadImage('soviet_soldier_prone','images/humans/russian_soldier_prone.png')
    world.graphic_engine.loadImage('soviet_dead','images/humans/russian_dead.png')
    
    # not used at the moment
    world.graphic_engine.loadImage('zombie_soldier','images/humans/zombie_soldier.png')
    
    world.graphic_engine.loadImage('civilian_man','images/humans/civilian_man.png')
    world.graphic_engine.loadImage('civilian_prone','images/humans/civilian_prone.png')
    world.graphic_engine.loadImage('civilian_dead','images/humans/civilian_dead.png')

    # guns
    world.graphic_engine.loadImage('1911','images/weapons/1911.png')
    world.graphic_engine.loadImage('dp28','images/weapons/dp28.png')
    world.graphic_engine.loadImage('mp40','images/weapons/mp40.png')
    world.graphic_engine.loadImage('ppk','images/weapons/ppk.png')
    world.graphic_engine.loadImage('stg44','images/weapons/stg44.png')
    world.graphic_engine.loadImage('tt33','images/weapons/tt33.png')
    world.graphic_engine.loadImage('kar98k','images/weapons/kar98k.png')
    world.graphic_engine.loadImage('mg34','images/weapons/mg34.png')
    world.graphic_engine.loadImage('mosin_nagant','images/weapons/mosin_nagant.png')
    world.graphic_engine.loadImage('ppsh43','images/weapons/ppsh43.png')
    world.graphic_engine.loadImage('k43','images/weapons/k43.png')
    world.graphic_engine.loadImage('g41w','images/weapons/g41-walther.png')
    world.graphic_engine.loadImage('fg42-type1','images/weapons/fg42-type1.png')
    world.graphic_engine.loadImage('fg42-type2','images/weapons/fg42-type2.png')
    world.graphic_engine.loadImage('svt40','images/weapons/svt40.png')
    world.graphic_engine.loadImage('svt40','images/weapons/svt40-sniper.png')

    # weapon magazines
    world.graphic_engine.loadImage('stg44_magazine','images/weapons/magazines/stg44_magazine.png')

    # shovels 
    world.graphic_engine.loadImage('german_folding_shovel','images/shovels/german_folding_shovel.png')
    world.graphic_engine.loadImage('german_field_shovel','images/shovels/german_field_shovel.png')
    

    # airplanes
    world.graphic_engine.loadImage('ju88-winter-weathered','images/airplanes/ju88-winter-weathered.png')

    # grenades
    world.graphic_engine.loadImage('model24','images/weapons/model24.png')

    # at rockets
    world.graphic_engine.loadImage('panzerfaust','images/weapons/panzerfaust.png')
    world.graphic_engine.loadImage('panzerfaust_warhead','images/projectiles/panzerfaust_warhead.png')

    # projectiles
    world.graphic_engine.loadImage('projectile','images/projectiles/projectile.png')
    world.graphic_engine.loadImage('shrapnel','images/projectiles/shrapnel.png')

    # buildings
    world.graphic_engine.loadImage('warehouse-inside','images/buildings/warehouse-inside.png')
    world.graphic_engine.loadImage('warehouse-outside','images/buildings/warehouse-outside.png')
    world.graphic_engine.loadImage('square_building_inside','images/buildings/square_building_inside.png')
    world.graphic_engine.loadImage('square_building_outside','images/buildings/square_building_outside.png')

    # vehicle
    world.graphic_engine.loadImage('kubelwagen','images/vehicles/kubelwagen/kubelwagen.png')
    world.graphic_engine.loadImage('kubelwagen_destroyed','images/vehicles/kubelwagen/kubelwagen_destroyed.png')
    world.graphic_engine.loadImage('red_bicycle','images/vehicles/bicycle/red_bicycle.png')

    #terrain
    world.graphic_engine.loadImage('catgrass','images/catgrass.png')

    #containers
    world.graphic_engine.loadImage('crate','images/containers/crate.png')
    world.graphic_engine.loadImage('small_crate','images/containers/small_crate.png')
    world.graphic_engine.loadImage('german_mg_ammo_can','images/containers/german_mg_ammo_can.png')
    world.graphic_engine.loadImage('german_fuel_can','images/containers/german_fuel_can.png')
    world.graphic_engine.loadImage('55_gallon_drum','images/containers/55_gal_drum.png')
    world.graphic_engine.loadImage('german_drop_canister','images/containers/german_drop_canister.png')

    # effects (sprites)
    world.graphic_engine.loadImage('blood_splatter','images/sprites/blood_splatter.png')
    world.graphic_engine.loadImage('small_blood','images/sprites/small_blood.png')
    world.graphic_engine.loadImage('brass','images/sprites/brass.png')
    # regular dirt was cool but it was huge. may use in future
    world.graphic_engine.loadImage('dirt','images/sprites/small_dirt.png')

    # consumables
    world.graphic_engine.loadImage('adler-cheese','images/consumables/adler-cheese.png')
    world.graphic_engine.loadImage('camembert-cheese','images/consumables/camembert-cheese.png')
    world.graphic_engine.loadImage('champignon-cheese','images/consumables/champignon-cheese.png')
    world.graphic_engine.loadImage('karwendel-cheese','images/consumables/karwendel-cheese.png')
    world.graphic_engine.loadImage('green_apple','images/consumables/green_apple.png')
    world.graphic_engine.loadImage('potato','images/consumables/potato.png')
    world.graphic_engine.loadImage('turnip','images/consumables/turnip.png')
    world.graphic_engine.loadImage('wine_bottle','images/consumables/wine_bottle.png')
    world.graphic_engine.loadImage('schokakola','images/consumables/schokakola.png')

    # random 
    world.graphic_engine.loadImage('map_pointer_green','images/map/map_pointer_green.png')
    world.graphic_engine.loadImage('map_pointer_blue','images/map/map_pointer_blue.png')
    world.graphic_engine.loadImage('map_pointer_orange','images/map/map_pointer_orange.png')

    # medical 
    world.graphic_engine.loadImage('bandage','images/medical/bandage.png')
    world.graphic_engine.loadImage('german_officer_first_aid_kit','images/medical/german_officer_first_aid_kit.png')

    # furniture 
    world.graphic_engine.loadImage('brown_chair','images/furniture/brown_chair.png')

    # engines 
    world.graphic_engine.loadImage('volkswagen_type_82_engine','images/engines/volkswagen_type_82_engine.png')
    world.graphic_engine.loadImage('bicycle_pedals','images/engines/bicycle_pedals.png')

    # fuel tanks 
    world.graphic_engine.loadImage('vehicle_fuel_tank','images/fuel_tanks/vehicle_fuel_tank.png')

#------------------------------------------------------------------------------
def load_magazine(world,magazine):
    '''loads a magazine with bullets'''
    count=0
    while count<magazine.ai.capacity:
        z=spawn_object(world,[0,0],'projectile',False)
        z.ai.projectile_type=magazine.ai.compatible_projectiles[0]
        magazine.ai.projectiles.append(z)

        count+=1

#------------------------------------------------------------------------------
def load_test_environment(world):
    ''' test environment. not a normal map load '''

    # setup spawn points 
    world.soviet_ai.spawn_points.append(world.spawn_east)
    world.american_ai.spawn_points.append(world.spawn_north)
    world.german_ai.spawn_points.append(world.spawn_west) 
    # civilian spawn points are generated 

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

    # add germans
    add_standard_squad(world,'german 1944 rifle')
    add_standard_squad(world,'german 1944 rifle')
    add_standard_squad(world,'german 1944 rifle')
    add_standard_squad(world,'german 1944 volksgrenadier fire group')

    # add soviets
    add_standard_squad(world,'soviet 1943 rifle')
    add_standard_squad(world,'soviet 1943 rifle')
    add_standard_squad(world,'soviet 1944 submachine gun')
    add_standard_squad(world,'soviet 1944 rifle')

    #---------misc stuff for testing ---------

    #spawn_object(world,[float(random.randint(0,0)),float(random.randint(0,0))],"55_gallon_drum",True)


    # add ju88
    spawn_object(world,[float(random.randint(-500,500)),float(random.randint(-500,500))],'ju88',True)

    

    # bikes 
    #spawn_object(world,[float(random.randint(-1500,1500)),float(random.randint(-1500,1500))],'red_bicycle',True)
  

#------------------------------------------------------------------------------
def spawn_civilians(WORLD,CIVILIAN_TYPE):
    ''' return a civilian with full kit '''
    # --------- german types ---------------------------------
    if CIVILIAN_TYPE=='default':
        z=spawn_object(WORLD,[0.0],'civilian_man',False)
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        return z
    if CIVILIAN_TYPE=='pistol':
        z=spawn_object(WORLD,[0.0],'civilian_man',False)
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppk',False))
        return z
    if CIVILIAN_TYPE=='big cheese':
        '''goofy unique civilain. don't mess with big cheese'''
        z=spawn_object(WORLD,[0.0],'civilian_man',False)
        z.ai.health*=2
        z.name='big cheese'
        z.world_builder_identity='civilian_default'
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'adler-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'camembert-cheese',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'panzerfaust',False))
        return z

#------------------------------------------------------------------------------
# currently used for wrecks and bodies
def spawn_container(NAME,WORLD,WORLD_COORDS,ROTATION_ANGLE,IMAGE,INVENTORY):
    '''spawns a custom container'''

    z=WorldObject(WORLD,[IMAGE],AIContainer)
    z.is_object_container=True
    z.render_level=2
    z.name=NAME
    z.world_coords=WORLD_COORDS
    z.rotation_angle=ROTATION_ANGLE
    z.ai.inventory=INVENTORY
    z.world_builder_identity='skip'
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_crate(WORLD,WORLD_COORDS,CRATE_TYPE):
    ''' generates different crate types with contents'''

    if CRATE_TYPE=='mp40':
        z=spawn_object(WORLD,WORLD_COORDS,'crate',True)
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'mp40',False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'mp40',False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'mp40',False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'mp40',False))
    elif CRATE_TYPE=="random_consumables":
        z=spawn_object(WORLD,WORLD_COORDS,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables,False))
    elif CRATE_TYPE=="random_consumables_common":
        z=spawn_object(WORLD,WORLD_COORDS,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
    elif CRATE_TYPE=="random_consumables_rare":
        z=spawn_object(WORLD,WORLD_COORDS,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_rare,False))
    elif CRATE_TYPE=="random_consumables_ultra_rare":
        z=spawn_object(WORLD,WORLD_COORDS,'small_crate',True)
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_ultra_rare,False))
    elif CRATE_TYPE=="random_guns":
        z=spawn_object(WORLD,WORLD_COORDS,'crate',True)
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_guns,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_guns,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_guns,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_guns,False))
    elif CRATE_TYPE=='panzerfaust':
        z=spawn_object(WORLD,WORLD_COORDS,'crate',True)
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'panzerfaust',False))
    elif CRATE_TYPE=='random_one_gun_type':
        z=spawn_object(WORLD,WORLD_COORDS,'crate',True)
        index=random.randint(0,len(list_guns)-1)
        amount= random.randint(1,6)
        for x in range(amount):
             z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,list_guns[index],False))

#------------------------------------------------------------------------------
def spawn_drop_canister(WORLD,WORLD_COORDS,CRATE_TYPE):
    ''' generates different crate types with contents'''

    z=spawn_object(WORLD,WORLD_COORDS,'german_drop_canister',True)


    if CRATE_TYPE=='mixed_supply':
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_german_guns,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_german_guns,False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'panzerfaust',False))
        z.ai.inventory.append(spawn_object(WORLD,WORLD_COORDS,'panzerfaust',False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_consumables_common,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_medical,False))
        z.ai.inventory.append(get_random_from_list(WORLD,WORLD_COORDS,list_medical,False))


  
#------------------------------------------------------------------------------
def spawn_object(WORLD,WORLD_COORDS,OBJECT_TYPE, SPAWN):
    '''returns new object. optionally spawns it in the world'''
    z=None
    if OBJECT_TYPE=='warehouse':
        z=WorldObject(WORLD,['warehouse-outside','warehouse-inside'],AIBuilding)
        z.name='warehouse'
        z.render_level=1
        z.collision_radius=200
        z.is_building=True

    elif OBJECT_TYPE=='square_building':
        z=WorldObject(WORLD,['square_building_outside','square_building_inside'],AIBuilding)
        z.name='square building'
        z.render_level=1
        z.collision_radius=60
        z.is_building=True

    elif OBJECT_TYPE=='green_apple':
        z=WorldObject(WORLD,['green_apple'],AIConsumable)
        z.render_level=2
        z.name='Green Apple'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-10 

    elif OBJECT_TYPE=='potato':
        z=WorldObject(WORLD,['potato'],AIConsumable)
        z.render_level=2
        z.name='potato'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-70
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-20  

    elif OBJECT_TYPE=='turnip':
        z=WorldObject(WORLD,['turnip'],AIConsumable)
        z.render_level=2
        z.name='turnip'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-60
        z.ai.thirst_effect=-8
        z.ai.fatigue_effect=-10  

    elif OBJECT_TYPE=='adler-cheese':
        z=WorldObject(WORLD,['adler-cheese'],AIConsumable)
        z.render_level=2
        z.name='Adler cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-200
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='camembert-cheese':
        z=WorldObject(WORLD,['camembert-cheese'],AIConsumable)
        z.render_level=2
        z.name='Camembert cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-250
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='champignon-cheese':
        z=WorldObject(WORLD,['champignon-cheese'],AIConsumable)
        z.render_level=2
        z.name='Champignon cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-300
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='karwendel-cheese':
        z=WorldObject(WORLD,['karwendel-cheese'],AIConsumable)
        z.render_level=2
        z.name='Karwendel cheese'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-500
        z.ai.thirst_effect=-5
        z.ai.fatigue_effect=-50  

    elif OBJECT_TYPE=='wine':
        z=WorldObject(WORLD,['wine_bottle'],AIConsumable)
        z.render_level=2
        z.name='wine'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=5
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=-500
        z.ai.fatigue_effect=50  

    elif OBJECT_TYPE=='schokakola':
        z=WorldObject(WORLD,['schokakola'],AIConsumable)
        z.render_level=2
        z.name='scho-ka-kola'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_consumable=True
        z.ai.health_effect=15
        z.ai.hunger_effect=-50
        z.ai.thirst_effect=10
        z.ai.fatigue_effect=-250 
    elif OBJECT_TYPE=='bandage':
        z=WorldObject(WORLD,['bandage'],AIMedical)
        z.render_level=2
        z.name='bandage'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=50
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=0
    elif OBJECT_TYPE=='german_officer_first_aid_kit':
        z=WorldObject(WORLD,['german_officer_first_aid_kit'],AIMedical)
        z.render_level=2
        z.name='German Officer First Aid Kit'
        z.rotation_angle=float(random.randint(0,359)) 
        z.is_medical=True
        z.ai.health_effect=150
        z.ai.hunger_effect=0
        z.ai.thirst_effect=0
        z.ai.fatigue_effect=-300  

    elif OBJECT_TYPE=='german_fuel_can':
        z=WorldObject(WORLD,['german_fuel_can'],AILiquidContainer)
        z.is_object_container=False # going to be something special
        z.is_liquid_container=True
        z.is_large_human_pickup=True
        z.ai.total_volume=20
        z.ai.used_volume=20
        z.ai.liquid_type='gas'
        z.ai.health_effect=-150
        z.ai.hunger_effect=100
        z.ai.thirst_effect=100
        z.ai.fatigue_effect=500  
        z.render_level=2
        z.name='german_fuel_can'
        z.world_builder_identity='german_fuel_can'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='55_gallon_drum':
        z=WorldObject(WORLD,['55_gallon_drum'],AILiquidContainer)
        z.is_liquid_container=True
        z.ai.total_volume=208
        z.ai.used_volume=208
        z.ai.liquid_type='gas'
        z.ai.health_effect=-150
        z.ai.hunger_effect=100
        z.ai.thirst_effect=100
        z.ai.fatigue_effect=500  
        z.render_level=2
        z.name='55_gallon_drum'
        z.collision_radius=15
        z.world_builder_identity='55_gallon_drum'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='german_mg_ammo_can':
        z=WorldObject(WORLD,['german_mg_ammo_can'],AIContainer)
        z.is_ammo_container=True
        z.is_large_human_pickup=True
        z.render_level=2
        z.name='german_mg_ammo_can'
        z.world_builder_identity='german_mg_ammo_can'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='german_drop_canister':
        z=WorldObject(WORLD,['german_drop_canister'],AIContainer)
        z.is_object_container=True
        z.is_large_human_pickup=True
        z.render_level=2
        z.name='german drop canister'
        z.collision_radius=20
        z.world_builder_identity='german_drop_canister'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='crate':
        z=WorldObject(WORLD,['crate'],AIContainer)
        z.is_object_container=True
        z.is_large_human_pickup=True
        z.render_level=2
        z.name='crate'
        z.collision_radius=20
        z.world_builder_identity='crate'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='small_crate':
        z=WorldObject(WORLD,['small_crate'],AIContainer)
        z.is_object_container=True
        z.is_large_human_pickup=True
        z.render_level=2
        z.name='small_crate'
        z.collision_radius=20
        z.world_builder_identity='small_crate'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='panzerfaust':
        z=WorldObject(WORLD,['panzerfaust'],AIGun)
        z.name='panzerfaust'
        z.render_level=2
        z.ai.speed=300
        z.is_handheld_antitank=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'panzerfaust_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=0
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='antitank launcher'
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='panzerfaust_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='panzerfaust_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['panzerfaust']
        z.ai.compatible_projectiles=['panzerfaust_60']
        z.ai.capacity=1
        z.ai.removable=False
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        p=spawn_object(WORLD,[0,0],'projectile',False)
        p.image_list=['panzerfaust_warhead']
        p.ai.projectile_type='panzerfaust_60'
        z.ai.projectiles.append(p)



    elif OBJECT_TYPE=='model24':
        z=WorldObject(WORLD,['model24'],AIThrowable)
        z.name='model24'
        z.is_grenade=True
        z.is_throwable=True
        z.ai.explosive=True
        z.ai.speed=110
        z.ai.max_speed=110
        z.ai.maxTime=3.3
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mp40':
        z=WorldObject(WORLD,['mp40'],AIGun)
        z.name='mp40'
        z.world_builder_identity='gun_mp40'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'mp40_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mp40_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='mp40_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mp40']
        z.ai.compatible_projectiles=['9mm_124','9mm_115','9mm_ME']
        z.ai.capacity=32
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='ppsh43':
        z=WorldObject(WORLD,['ppsh43'],AIGun)
        z.name='ppsh43'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'ppsh43_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=7
        z.ai.flight_time=2
        z.ai.range=700
        z.ai.type='submachine gun'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ppsh43_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='ppsh43_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppsh43']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=35
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='stg44':
        z=WorldObject(WORLD,['stg44'],AIGun)
        z.name='stg44'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'stg44_magazine',False)
        z.ai.rate_of_fire=0.1
        z.ai.reload_speed=7
        z.ai.flight_time=2.5
        z.ai.range=800
        z.ai.type='assault rifle'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
    
    elif OBJECT_TYPE=='stg44_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='stg44_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['stg44']
        z.ai.compatible_projectiles=['7.92x33_SME']
        z.ai.capacity=30
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='dp28':
        z=WorldObject(WORLD,['dp28'],AIGun)
        z.name='dp28'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'dp28_magazine',False)
        z.ai.rate_of_fire=0.12
        z.ai.reload_speed=30
        z.ai.flight_time=3.5
        z.ai.range=800
        z.ai.type='machine gun'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='dp28_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='dp28_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['dp28']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=47
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='ppk':
        z=WorldObject(WORLD,['ppk'],AIGun)
        z.name='ppk'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'ppk_magazine',False)
        z.ai.rate_of_fire=0.7
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    # NOTE - this should be 32 ACP or something
    elif OBJECT_TYPE=='ppk_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='ppk_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['ppk']
        z.ai.compatible_projectiles=['9mm_ME']
        z.ai.capacity=8
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='tt33':
        z=WorldObject(WORLD,['tt33'],AIGun)
        z.name='tt33'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'tt33_magazine',False)
        z.ai.rate_of_fire=0.9
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='tt33_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='tt33_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['tt33']
        z.ai.compatible_projectiles=['7.62x25']
        z.ai.capacity=8
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='1911':
        z=WorldObject(WORLD,['1911'],AIGun)
        z.name='1911'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'1911_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=5
        z.ai.flight_time=1
        z.ai.range=380
        z.ai.type='pistol'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
    
    elif OBJECT_TYPE=='1911_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='1911_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['1911']
        z.ai.compatible_projectiles=['45acp']
        z.ai.capacity=7
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)


    elif OBJECT_TYPE=='mg34':
        z=WorldObject(WORLD,['mg34'],AIGun)
        z.name='mg34'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'mg34_drum_magazine',False)
        z.ai.rate_of_fire=0.05
        z.ai.reload_speed=13
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='machine gun'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mg34_drum_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='mg34_drum_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mg34']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=75
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='kar98k':
        z=WorldObject(WORLD,['kar98k'],AIGun)
        z.name='kar98k'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'kar98k_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=10
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='kar98k_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='kar98k_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['kar98k']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=5
        z.ai.removable=False
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='g41w':
        z=WorldObject(WORLD,['g41w'],AIGun)
        z.name='g41w'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'g41w_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='g41w_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='g41w_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['g41w']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='k43':
        z=WorldObject(WORLD,['k43'],AIGun)
        z.name='k43'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'k43_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='k43_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='k43_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['k43']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=10
        z.ai.removable=True
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='fg42-type1':
        z=WorldObject(WORLD,['fg42-type1'],AIGun)
        z.name='fg42-type1'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'fg42_type1_magazine',False)
        z.ai.rate_of_fire=0.06
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='fg42_type1_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='fg42_type1_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type1']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='fg42-type2':
        z=WorldObject(WORLD,['fg42-type2'],AIGun)
        z.name='fg42-type2'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'fg42_type2_magazine',False)
        z.ai.rate_of_fire=0.08
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='fg42_type2_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='fg42_type2_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['fg42-type2']
        z.ai.compatible_projectiles=['7.92x57_SSP','7.92x57_SME','7.92x57_SMK','7.92x57_SMKH']
        z.ai.capacity=20
        z.ai.removable=True
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='mosin_nagant':
        z=WorldObject(WORLD,['mosin_nagant'],AIGun)
        z.name='mosin_nagant'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'mosin_magazine',False)
        z.ai.rate_of_fire=1.1
        z.ai.reload_speed=11
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='mosin_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='mosin_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['mosin_nagant']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=5
        z.ai.removable=False
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)
    
    elif OBJECT_TYPE=='svt40':
        z=WorldObject(WORLD,['svt40'],AIGun)
        z.name='svt40'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'svt40_magazine',False)
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=7
        z.ai.flight_time=3
        z.ai.range=800
        z.ai.type='rifle'
        z.ai.projectile_type='7.62x54_L'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='svt40_magazine':
        z=WorldObject(WORLD,['stg44_magazine'],AIMagazine)
        z.name='svt40_magazine'
        z.is_gun_magazine=True
        z.ai.compatible_guns=['svt40','svt40-sniper']
        z.ai.compatible_projectiles=['7.62x54_L','7.62x54_D']
        z.ai.capacity=10
        z.ai.removable=True
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))
        load_magazine(WORLD,z)

    elif OBJECT_TYPE=='svt40-sniper':
        z=WorldObject(WORLD,['svt40-sniper'],AIGun)
        z.name='svt40-sniper'
        z.is_gun=True
        z.ai.magazine=spawn_object(WORLD,[0,0],'svt40_magazine',False)
        z.ai.mag_capacity=10
        z.ai.magazine_count=6
        z.ai.max_magazines=6
        z.ai.rate_of_fire=0.8
        z.ai.reload_speed=8
        z.ai.flight_time=3.5
        z.ai.range=850
        z.ai.type='rifle'
        z.ai.projectile_type='7.62x54_L'
        z.render_level=2
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='kubelwagen':
        z=WorldObject(WORLD,['kubelwagen','kubelwagen_destroyed'],AIVehicle)
        z.name='kubelwagen'
        z.is_vehicle=True
        z.render_level=3
        z.ai.max_speed=200
        z.ai.rotation_speed=40.
        z.collision_radius=50
        z.weight=800
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=3
        z.ai.fuel_tanks.append(spawn_object(WORLD,[0,0],"vehicle_fuel_tank",False))
        z.ai.engines.append(spawn_object(WORLD,[0,0],"volkswagen_type_82_engine",False))
        
        if random.randint(0,3)==1:
            mg=spawn_object(WORLD,[0,0],'mg34',False)
            z.ai.primary_weapon=mg
            z.add_inventory(mg)
            z.add_inventory(spawn_object(WORLD,[0,0],"german_mg_ammo_can",False))
        z.add_inventory(spawn_object(WORLD,[0,0],"german_fuel_can",False))
        z.add_inventory(get_random_from_list(WORLD,WORLD_COORDS,list_medical,False))
        z.add_inventory(get_random_from_list(WORLD,WORLD_COORDS,list_german_military_equipment,False))
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='red_bicycle':
        # note second image is used for the wreck..
        z=WorldObject(WORLD,['red_bicycle','red_bicycle'],AIVehicle)
        z.name='red_bicycle'
        z.is_vehicle=True
        z.render_level=3
        z.ai.max_speed=100
        z.ai.rotation_speed=50.
        z.ai.max_occupants=1
        z.ai.open_top=True
        z.collision_radius=50
        z.ai.engines.append(spawn_object(WORLD,[0,0],"bicycle_pedals",False))
        z.weight=13
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=3

        if random.randint(0,3)==1:
            z.add_inventory(get_random_from_list(WORLD,WORLD_COORDS,list_consumables,False))
        z.rotation_angle=float(random.randint(0,359))

    elif OBJECT_TYPE=='ju88':
        z=WorldObject(WORLD,['ju88-winter-weathered'],AIVehicle)
        z.name='Junkers Ju88'
        z.ai.max_speed=500
        z.ai.rotation_speed=50
        z.ai.acceleration=100
        z.render_level=3
        z.collision_radius=200
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34',False)) 
        z.is_airplane=True 
        z.rotation_angle=float(random.randint(0,359))
        z.weight=800
        z.rolling_resistance=0.015
        z.drag_coefficient=0.8
        z.frontal_area=3
        z.ai.fuel_tanks.append(spawn_object(WORLD,[0,0],"vehicle_fuel_tank",False))
        z.ai.engines.append(spawn_object(WORLD,[0,0],"volkswagen_type_82_engine",False))

    # this is only used briefly until the player picks a spawn type
    # this is required because a lot of stuff in the game references the player object.
    elif OBJECT_TYPE=='player':
        z=WorldObject(WORLD,['man','civilian_prone','civilian_dead'],AIHuman)
        z.name='player'
        z.ai.speed=50.
        z.is_player=True
        z.render_level=4
        z.is_human=True
        WORLD.player=z

    elif OBJECT_TYPE=='civilian_man':
        z=WorldObject(WORLD,['civilian_man','civilian_prone','civilian_dead'],AIHuman)
        z.name=engine.name_gen.generate('civilian')
        z.ai.speed=float(random.randint(10,25))
        z.render_level=4
        z.collision_radius=10
        z.is_human=True
        z.is_civilian=True

    elif OBJECT_TYPE=='german_soldier':
        z=WorldObject(WORLD,['german_soldier','german_soldier_prone','german_dead'],AIHuman)
        z.name=engine.name_gen.generate('german')
        z.ai.speed=float(random.randint(20,25))
        z.render_level=4
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_german=True

    elif OBJECT_TYPE=='soviet_soldier':
        z=WorldObject(WORLD,['soviet_soldier','soviet_soldier_prone','soviet_dead'],AIHuman)
        z.name=engine.name_gen.generate('soviet')
        z.ai.speed=float(random.randint(20,25))
        z.render_level=4
        z.collision_radius=10
        z.is_human=True
        z.is_soldier=True
        z.is_soviet=True

    elif OBJECT_TYPE=='brass':
        z=WorldObject(WORLD,['brass'],AINone)
        w=[WORLD_COORDS[0]+float(random.randint(-7,7)),WORLD_COORDS[1]+float(random.randint(-7,7))]
        z.world_coords=copy.copy(w)
        z.render_level=2
        z.name='brass'
        z.rotation_angle=float(random.randint(0,359))  
    
    elif OBJECT_TYPE=='blood_splatter':
        z=WorldObject(WORLD,['blood_splatter'],AINone)
        z.render_level=2
        z.name='blood_splatter'
        z.rotation_angle=float(random.randint(0,359))  

    elif OBJECT_TYPE=='small_blood':
        z=WorldObject(WORLD,['small_blood'],AINone)
        z.render_level=2
        z.name='small_blood'
        z.rotation_angle=float(random.randint(0,359)) 
           
    elif OBJECT_TYPE=='dirt':
        z=WorldObject(WORLD,['dirt'],AINone)
        z.render_level=2
        z.name='dirt'
        z.rotation_angle=float(random.randint(0,359))
    
    elif OBJECT_TYPE=='brown_chair':
        z=WorldObject(WORLD,['brown_chair'],AINone)
        z.render_level=2
        z.name='brown_chair'
        z.is_furniture=True
        z.is_large_human_pickup=True
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='german_field_shovel':
        z=WorldObject(WORLD,['german_field_shovel'],AIThrowable)
        z.render_level=2
        z.name='german field shovel'
        z.is_throwable=True
        z.ai.speed=90.
        z.ai.max_speed=90
        z.ai.maxTime=3
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='german_folding_shovel':
        z=WorldObject(WORLD,['german_folding_shovel'],AIThrowable)
        z.render_level=2
        z.name='german folding shovel'
        z.is_throwable=True
        z.ai.speed=90.
        z.ai.max_speed=90
        z.ai.maxTime=3
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='volkswagen_type_82_engine':
        z=WorldObject(WORLD,['volkswagen_type_82_engine'],AIEngine)
        z.render_level=2
        z.name='Volkswagen Type 82 Engine'
        z.ai.fuel_type='gas'
        z.ai.fuel_consumption_rate=0.0033
        z.ai.max_engine_force=25277.9
        z.rotation_angle=float(random.randint(0,359)) 
    elif OBJECT_TYPE=='vehicle_fuel_tank':
        z=WorldObject(WORLD,['vehicle_fuel_tank'],AILiquidContainer)
        z.is_liquid_container=True
        z.ai.total_volume=20
        z.ai.used_volume=20
        z.ai.liquid_type='gas'
        z.ai.health_effect=-150
        z.ai.hunger_effect=100
        z.ai.thirst_effect=100
        z.ai.fatigue_effect=500  
        z.render_level=2
        z.name='vehicle_fuel_tank'
        z.world_builder_identity='vehicle_fuel_tank'
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='bicycle_pedals':
        z=WorldObject(WORLD,['bicycle_pedals'],AIEngine)
        z.render_level=2
        z.name='bicycle pedals'
        z.ai.fuel_type='none'
        z.ai.fuel_consumption_rate=0
        z.ai.max_engine_force=131.44
        z.ai.engine_on=True
        z.rotation_angle=float(random.randint(0,359))
    elif OBJECT_TYPE=='projectile':
        z=WorldObject(WORLD,['projectile'],AIProjectile)
        z.name='projectile'
        z.ai.speed=350.
        z.is_projectile=True
        z.render_level=3
        #z.ai.projectile_type=PROJECTILE_TYPE

    else:
        print('!! Spawn Error: '+OBJECT_TYPE+' is not recognized.')  

    # -- generic settings that apply to all --
    z.world_builder_identity=OBJECT_TYPE
    # set world coords if they weren't already set
    if z.world_coords==None:
        z.world_coords=copy.copy(WORLD_COORDS)

    if SPAWN :
        z.wo_start()
    return z


#------------------------------------------------------------------------------
def spawn_map_pointer(WORLD,TARGET_COORDS,TYPE):
    if TYPE=='normal':
        z=WorldObject(WORLD,['map_pointer_green'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()
    if TYPE=='blue':
        z=WorldObject(WORLD,['map_pointer_blue'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()
    if TYPE=='orange':
        z=WorldObject(WORLD,['map_pointer_orange'],AIMapPointer)
        z.ai.target_coords=TARGET_COORDS
        z.render_level=4
        z.is_map_pointer=True
        z.wo_start()



#------------------------------------------------------------------------------
# basically just a different kind of projectile
def spawn_shrapnel(WORLD,WORLD_COORDS,TARGET_COORDS,IGNORE_LIST,PROJECTILE_TYPE,MIN_TIME,MAX_TIME,ORIGINATOR,WEAPON_NAME):
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z=WorldObject(WORLD,['shrapnel'],AIProjectile)
    z.name='shrapnel'
    z.world_coords=copy.copy(WORLD_COORDS)
    z.ai.speed=300.
    z.ai.maxTime=random.uniform(MIN_TIME, MAX_TIME)
    z.is_projectile=True
    z.render_level=3
    z.ai.ignore_list=copy.copy(IGNORE_LIST)
    z.ai.projectile_type=PROJECTILE_TYPE
    z.rotation_angle=engine.math_2d.get_rotation(WORLD_COORDS,TARGET_COORDS)
    z.heading=engine.math_2d.get_heading_vector(WORLD_COORDS,TARGET_COORDS)
    # increase the collision radius to make sure we get hits
    z.collision_radius=10
    z.ai.shooter=ORIGINATOR
    z.ai.weapon_name=WEAPON_NAME
    z.wo_start()

#------------------------------------------------------------------------------
def spawn_shrapnel_cloud(WORLD,WORLD_COORDS,AMOUNT,ORIGINATOR,WEAPON_NAME):
    ''' creates a shrapnel starburst pattern. used for grenades '''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    ignore_list=[]
    if WORLD.friendly_fire_explosive==False:
        if ORIGINATOR.is_german:
                ignore_list+=WORLD.wo_objects_german
        elif ORIGINATOR.is_soviet:
            ignore_list+=WORLD.wo_objects_soviet
        elif ORIGINATOR.is_american:
            ignore_list+=WORLD.wo_objects_american
    elif WORLD.friendly_fire_explosive_squad==False:
        # just add the squad
        ignore_list+=ORIGINATOR.ai.squad.members

    for x in range(AMOUNT):
        target_coords=[float(random.randint(-150,150))+WORLD_COORDS[0],float(random.randint(-150,150))+WORLD_COORDS[1]]
        spawn_shrapnel(WORLD,WORLD_COORDS,target_coords,ignore_list,'shrapnel',0.1,0.4,ORIGINATOR,WEAPON_NAME)

#------------------------------------------------------------------------------
def spawn_heat_jet(WORLD,WORLD_COORDS,TARGET_COORDS,AMOUNT,ORIGINATOR,WEAPON_NAME):
    ''' creates a cone/line of shrapnel. used for panzerfaust'''
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    for x in range(AMOUNT):
        target_coords=[float(random.randint(-5,5))+TARGET_COORDS[0],float(random.randint(-5,5))+TARGET_COORDS[1]]
        spawn_shrapnel(WORLD,WORLD_COORDS,target_coords,[],'HEAT_jet',0.1,0.3,ORIGINATOR,WEAPON_NAME)


#------------------------------------------------------------------------------
def spawn_soldiers(WORLD,SOLDIER_TYPE):
    ''' return a soldier with full kit '''
    # --------- german types ---------------------------------
    if SOLDIER_TYPE=='german_kar98k':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_kar98k'
        z.add_inventory(spawn_object(WORLD,[0,0],'kar98k',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'kar98k_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'kar98k_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'kar98k_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'kar98k_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'kar98k_magazine',False))
        return z
    if SOLDIER_TYPE=='german_k43':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_k43'
        z.add_inventory(spawn_object(WORLD,[0,0],'k43',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'k43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'k43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'k43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'k43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'k43_magazine',False))
        return z
    if SOLDIER_TYPE=='german_g41w':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_g41w'
        z.add_inventory(spawn_object(WORLD,[0,0],'g41w',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'g41w_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'g41w_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'g41w_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'g41w_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'g41w_magazine',False))
        return z
    if SOLDIER_TYPE=='german_mp40':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_mp40'
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mp40_magazine',False))
        return z
    if SOLDIER_TYPE=='german_mg34':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_mg34'
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34_drum_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mg34_drum_magazine',False))
        return z
    if SOLDIER_TYPE=='german_stg44':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_stg44'
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'stg44_magazine',False))
        return z
    if SOLDIER_TYPE=='german_fg42-type2':
        z=spawn_object(WORLD,[0.0],'german_soldier',False)
        z.world_builder_identity='german_fg42-type2'
        z.add_inventory(spawn_object(WORLD,[0,0],'fg42-type2',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'fg42_type2_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'fg42_type2_magazine',False))
        return z

    # --------- soviet types ----------------------------------------
    if SOLDIER_TYPE=='soviet_mosin_nagant':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_mosin_nagant'
        z.add_inventory(spawn_object(WORLD,[0,0],'mosin_nagant',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mosin_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mosin_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mosin_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mosin_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'mosin_magazine',False))
        return z
    if SOLDIER_TYPE=='soviet_svt40':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_svt40'
        z.add_inventory(spawn_object(WORLD,[0,0],'svt40',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'svt40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'svt40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'svt40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'svt40_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'svt40_magazine',False))
        return z
    if SOLDIER_TYPE=='soviet_ppsh43':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_ppsh43'
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'ppsh43_magazine',False))
        return z 
    if SOLDIER_TYPE=='soviet_dp28':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_dp28'
        z.add_inventory(spawn_object(WORLD,[0,0],'dp28',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'dp28_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'dp28_magazine',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'dp28_magazine',False))
        return z 
    if SOLDIER_TYPE=='soviet_tt33':
        z=spawn_object(WORLD,[0.0],'soviet_soldier',False)
        z.world_builder_identity='soviet_tt33'
        z.add_inventory(spawn_object(WORLD,[0,0],'tt33',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'model24',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'bandage',False))
        z.add_inventory(spawn_object(WORLD,[0,0],'tt33_magazine',False)) 
        return z   
