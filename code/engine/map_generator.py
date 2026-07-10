'''
repo : https://github.com/openmarmot/twe

notes :
'''

# import built in modules
import random


# import custom modules 
from engine.map_object import MapObject
import engine.math_2d
import engine.world_builder
import engine.log
import math

#------------------------------------------------------------------------------
def generate_civilians(map_objects):
    '''generates and returns a array of civilian map_objects'''
    civilians=[]

    for b in map_objects:
        if b.world_builder_identity=='warehouse':
            count=random.randint(0,10)
            for _ in range(count):
                coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
                rotation=random.randint(0,359)
                civilians.append(MapObject('civilian_man','',coords,rotation,[]))

        elif b.world_builder_identity=='square_building':
            count=random.randint(1,3)
            for _ in range(count):
                coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
                rotation=random.randint(0,359)
                civilians.append(MapObject('civilian_man','',coords,rotation,[]))

    # unique civilian big cheese
    if random.randint(1,100)<5:
        coords=[random.randint(-1000,1000),random.randint(-1000,1000)]
        rotation=random.randint(0,359)
        civilians.append(MapObject('civilian_big_cheese','',coords,rotation,[]))
        engine.log.add_data('note','big_cheese added to map',True)

    # unique civilian shovel_man
    if random.randint(1,100)<5:
        coords=[random.randint(-1000,1000),random.randint(-1000,1000)]
        rotation=random.randint(0,359)
        civilians.append(MapObject('civilian_shovel_man','',coords,rotation,[]))
        engine.log.add_data('note','shovel_man added to map',True)

    # just in case there aren't any buildings of the right type
    if len(civilians)==0:
        count=random.randint(20,100)
        for _ in range(count):
            map_size=2000
            coords=[random.randint(-map_size,map_size),random.randint(-map_size,map_size)]
            rotation=random.randint(0,359)
            civilians.append(MapObject('civilian_man','',coords,rotation,[]))


    return civilians

#------------------------------------------------------------------------------
def generate_clutter(map_objects):
    '''generates and auto places small objects around the map'''
    # map_objects - array of map_objects
    # returns array of map_objects
    clutter=[]

    for b in map_objects:

        # industrial clutter
        if b.world_builder_identity=='warehouse':

            # - add crate with specific locations - 
            locations=[] # [position,rotation]
            locations.append([[36.0, 162.0],0])
            locations.append([[-30.0, 170.0],0])
            locations.append([[-85.0, 170.0],0])
            locations.append([[-150.0, 170.0],0])
            locations.append([[-86.0, 354.0],90])

            crate_amount=random.randint(1,3)
            for _ in range(crate_amount):
                location=locations.pop()
                coords=engine.math_2d.calculate_relative_position(b.world_coords,b.rotation,location[0])
                rotation=b.rotation+location[1]
                crate=random.choice(['crate','crate_mp40','crate_random_consumables'])
                clutter.append(MapObject(crate,'crate',coords,rotation,[]))

            # add other random stuff
            chance=random.randint(1,7)
            coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
            rotation=random.randint(0,359)
            if chance==1 or chance==2:
                clutter.append(MapObject('brown_chair','brown chair',coords,rotation,[]))
            if chance==1 or chance==3 or chance==4:
                # some overlap
                clutter.append(MapObject('cupboard','cupboard',coords,rotation,[]))
            if chance==5:
                clutter.append(MapObject('wood_log','wood log',coords,rotation,[]))
            if chance==6:
                clutter.append(MapObject('barrel','barrel',coords,rotation,[]))
            if chance==7:
                clutter.append(MapObject('red_bicycle','red bicycle',coords,rotation,[]))


        # house clutter 
        elif b.world_builder_identity=='square_building':

            # - add cupboard with specific locations - 
            cupboard_locations=[] # [position,rotation]
            cupboard_locations.append([[-46.0, 0.0],0])
            cupboard_locations.append([[-26.0, 48.0],90])
            cupboard_locations.append([[-33.0, -48.0],90])
            cupboard_locations.append([[9.0, -48.0],90])
            cupboard_locations.append([[31.0, -20.0],0])

            cupboard_amount=random.randint(1,2)
            for _ in range(cupboard_amount):
                location=cupboard_locations.pop()
                coords=engine.math_2d.calculate_relative_position(b.world_coords,b.rotation,location[0])
                rotation=b.rotation+location[1]
                clutter.append(MapObject('cupboard','cupboard',coords,rotation,[]))

            # - add other junk -
            chance=random.randint(1,8)
            coords=[b.world_coords[0]+random.randint(-20,20),b.world_coords[1]+random.randint(-20,20)]
            rotation=random.randint(0,359)
            if chance==1 or chance==2:
                clutter.append(MapObject('brown_chair','brown chair',coords,rotation,[]))
            if chance==5:
                clutter.append(MapObject('wood_log','wood log',coords,rotation,[]))
            if chance==6:
                clutter.append(MapObject('barrel','barrel',coords,rotation,[]))
            if chance==7:
                clutter.append(MapObject('red_bicycle','red bicycle',coords,rotation,[]))

    # add some crates 
                
    # add some vehicles 
                
    return clutter

#------------------------------------------------------------------------------
def generate_map(map_areas):
    '''
    entry point 
    generate a map. return a list of map objects

    map_areas : list of map areas to be created 
    options airport,rail_yard,town
    '''

    map_objects=[]

    min_world_size=20000

    world_size=max(min_world_size,len(map_areas)*4000)

    coord_list=engine.math_2d.get_random_constrained_coords_v2([0,0],8000,5000,len(map_areas),[],0) 
    for map_area in map_areas:
        if map_area=='airport':
            map_objects+=generate_map_area_airport(coord_list.pop(),'airport')
        elif map_area=='rail_yard':
            map_objects+=generate_map_area_rail_yard(coord_list.pop(),'rail_yard')
        elif map_area=='town':
            map_objects+=generate_map_area_town(coord_list.pop(),'town')

    # generate dynamic roads between towns
    map_objects+=generate_dynamic_roads(map_objects)
    roads=[o for o in map_objects if o.world_builder_identity=='road_300']
    for b in map_objects:
        if b.world_builder_identity in ('warehouse','square_building'):
            for r in roads:
                if engine.math_2d.get_distance(b.world_coords,r.world_coords)<180:
                    dx=b.world_coords[0]-r.world_coords[0]
                    dy=b.world_coords[1]-r.world_coords[1]
                    b.world_coords=[b.world_coords[0]+dx*0.3,b.world_coords[1]+dy*0.3]
                    break

    # generate clutter 
    map_objects+=generate_clutter(map_objects)

    # generate vegetation (new generator already avoids buildings + roads via sized exclusions)
    veg = generate_vegetation(map_objects, world_size)
    map_objects += veg

    # generate civilians
    map_objects+=generate_civilians(map_objects)

    # generate terrain 

    return map_objects


#------------------------------------------------------------------------------
def generate_map_area_airport(world_coords,name):
    map_objects=[]
    # create a long runway 
    count=400
    coords=engine.math_2d.get_column_coords(world_coords,80,count,270,4)
    for _ in range(count):
        map_objects.append(MapObject('concrete_square','',coords.pop(),random.choice([0,90,180,270]),[]))

    # add hangars
    map_objects.append(MapObject('hangar','hangar',[world_coords[0]+1500,world_coords[1]+600],0,[]))
    map_objects.append(MapObject('hangar','hangar',[world_coords[0]+2500,world_coords[1]+600],0,[]))
    map_objects.append(MapObject('hangar','hangar',[world_coords[0]+3500,world_coords[1]+600],0,[]))

    # add a world_area map object so the tactical ai can recognize it, and so it shows up on maps
    world_area=MapObject('world_area_'+'airport',name,world_coords,0,[])
    map_objects.append(world_area)

    return map_objects

#------------------------------------------------------------------------------
def generate_map_area_rail_yard(world_coords,name):
    '''generate rail yard map area'''
    engine.log.add_data('warn','world_builder.generate_world_area_rail_yard: not implemented',True)
    map_objects=[]

    # add a world_area map object so the tactical ai can recognize it, and so it shows up on maps
    world_area=MapObject('world_area_'+'rail_yard',name,world_coords,0,[])
    map_objects.append(world_area)
    return map_objects

#------------------------------------------------------------------------------
def generate_map_area_simple(world_coords,count,diameter,world_builder_identity,name,rotation):
    '''generates a simple one object type world area '''
    # count: int
    # diameter : int - rough size of the object
    coords=engine.math_2d.get_grid_coords(world_coords,diameter,count)
    map_objects=[]
    for _ in range(count):
        map_objects.append(MapObject(world_builder_identity,name,coords.pop(),rotation,[]))
    
    return map_objects

#------------------------------------------------------------------------------
def generate_map_area_town(world_coords,name):
    count_warehouse=random.randint(2,5)
    count_building=random.randint(2,14)
    
    map_objects=[]
    
    # add warehouses in a grid
    warehouse_seperation=850
    coords=engine.math_2d.get_grid_coords(world_coords,warehouse_seperation,count_warehouse)
    rotation=random.choice([0,90,180,270])
    coords_to_avoid=[]
    for _ in range(count_warehouse):
        warehouse_coord=coords.pop()
        coords_to_avoid.append(warehouse_coord)
        map_objects.append(MapObject('warehouse','old warehouse',warehouse_coord,rotation,[]))
    
    # add smaller square buildings in a more random pattern, avoiding the warehouses 
    building_max_area=3000
    building_seperation=200
    building_coords=engine.math_2d.get_random_constrained_coords_v2(world_coords,building_max_area,
        building_seperation,count_building,coords_to_avoid,warehouse_seperation)
    for _ in range(count_building):
        map_objects.append(MapObject('square_building','some sort of building',building_coords.pop(),rotation,[]))

    # add a world_area map object so the tactical ai can recognize it, and so it shows up on maps
    world_area=MapObject('world_area_'+'town',name,world_coords,0,[])
    map_objects.append(world_area)

    return map_objects

#------------------------------------------------------------------------------
def generate_road(start_coords,end_coords,road_type,segment_height):
    #road_type string, the world_builder_identity of the road segment
    # rotation is in degrees
    actual_rotation=engine.math_2d.get_rotation(start_coords,end_coords)
    actual_distance=engine.math_2d.get_distance(start_coords,end_coords)

    # for now calculated_rotation is the closest angle of 0,90,180,270
    #calculated_rotation = round(actual_rotation / 90) * 90 % 360

    # determine the number of segments needed and the overlap
    # overlap defaults to the segment type_height
    # if there is a remainder we will go one over and slightly overlap them
    number_of_segments = math.ceil(actual_distance / segment_height)

    segments=[]

    # fill out the segments array
    dir = engine.math_2d.get_heading_vector(start_coords, end_coords)
    for i in range(number_of_segments):
        center_pos = [start_coords[0] + (i * segment_height + segment_height / 2) * dir[0], 
                        start_coords[1] + (i * segment_height + segment_height / 2) * dir[1]]
        segments.append(MapObject(road_type,road_type,center_pos,actual_rotation,[]))

    return segments


#------------------------------------------------------------------------------
def generate_dynamic_roads(map_objects):
    towns=[obj for obj in map_objects if obj.world_builder_identity=='world_area_town']
    if len(towns)<=1: return []
    xs=[t.world_coords[0] for t in towns]
    ys=[t.world_coords[1] for t in towns]
    y_mean=sum(ys)/len(ys)
    x_min=min(xs)-2000
    x_max=max(xs)+2000
    roads=generate_road([x_min,y_mean],[x_max,y_mean],'road_300',300)
    for t in towns:
        offset=150 if t.world_coords[1]>y_mean else -150
        target=[t.world_coords[0],y_mean+offset]
        roads+=generate_road(t.world_coords,target,'road_300',300)
    return roads

#------------------------------------------------------------------------------
def generate_vegetation(map_objects,world_size):
    '''generates vegetation
    this should be run after buildings are created
    map_objects - list of existing map objects
    world_size - size of map in all directions. should be > than town generation size
    returns a list of vegetation map objects

    New implementation:
    - Much faster generation (cheap local rejection instead of many heavy
      get_random_constrained_* calls per forest clump).
    - Proper sized exclusion zones for buildings and (sampled) roads so vegetation
      does not overlap man-made features.
    - Designed so you can easily increase coverage/density by adjusting a handful
      of constants without the function becoming slow.
    '''
    vegetation = []
    half = world_size

    # Build sized exclusion zones once: (cx, cy, clearance_radius)
    # These radii are chosen to keep sprites from visually/physically overlapping
    # buildings, runways, and roads (with a little extra margin).
    exclusions = []  # (x, y, rad)
    building_clear = {
        'hangar': 620,
        'warehouse': 265,
        'square_building': 130,
        'concrete_square': 48,
    }
    ROAD_CLEAR = 148

    roads = []
    for obj in map_objects:
        wid = obj.world_builder_identity
        if wid in building_clear:
            c = obj.world_coords
            exclusions.append((c[0], c[1], building_clear[wid]))
        elif wid == 'road_300':
            roads.append(obj)

    for r in roads:
        # Sample a few points along each road segment for decent linear avoidance
        c = r.world_coords
        rot = getattr(r, 'rotation', 0)
        rad = math.radians(rot)
        hx = math.cos(rad)
        hy = math.sin(rad)
        for off in (-110.0, 0.0, 110.0):
            exclusions.append((c[0] + off * hx, c[1] + off * hy, ROAD_CLEAR))

    # Fast helpers (nested so they can see exclusions list)
    def _clear(x, y, margin):
        for cx, cy, rad in exclusions:
            dx = x - cx
            dy = y - cy
            if dx*dx + dy*dy < (rad + margin) * (rad + margin):
                return False
        return True

    def _pick_shape():
        # weighted: ovals/kidneys more common than plain circles
        return random.choices(
            ['circle', 'oval', 'kidney'], weights=[0.18, 0.42, 0.40])[0]

    def _sample_blob(cx, cy, major, minor, orient, shape, edge_bias=0.5):
        '''sample a point inside an oriented blob.
        edge_bias: 0.5 ~ area-uniform disk; higher packs toward edge; lower toward center.
        shape: circle | oval | kidney
        '''
        r = random.random() ** edge_bias
        t = random.random() * math.pi * 2
        ux = r * math.cos(t)
        uy = r * math.sin(t)
        if shape == 'circle':
            lx = ux * major
            ly = uy * major
        elif shape == 'oval':
            lx = ux * major
            ly = uy * minor
        else:
            # kidney / cashew: elongate, then bend so one long side is concave
            lx = ux * major * (0.78 + 0.22 * abs(uy))
            ly = uy * minor
            lx = lx + 0.52 * major * (uy * uy)
        ca = math.cos(orient)
        sa = math.sin(orient)
        return [cx + lx * ca - ly * sa, cy + lx * sa + ly * ca]

    def _blob_axes(size, shape):
        '''return (major, minor) radii for a given nominal size + shape'''
        if shape == 'circle':
            return size, size
        if shape == 'oval':
            aspect = random.uniform(0.38, 0.72)
            return size, size * aspect
        # kidney: fairly elongated
        aspect = random.uniform(0.42, 0.70)
        return size, size * aspect


    # --- 1. Small meadow clumps (never place solo terrain_green) ---
    # terrain_green has a square sprite that looks bad in isolation; always
    # place it in tight clumps so the pattern blends.
    MEADOW_CLUMPS = random.randint(55, 95)
    MEADOW_SEP = 420
    MEADOW_MARGIN = 28
    meadow_seeds = []
    m_att = 0
    m_max = MEADOW_CLUMPS * 40
    while len(meadow_seeds) < MEADOW_CLUMPS and m_att < m_max:
        m_att += 1
        mx = random.randint(-half, half)
        my = random.randint(-half, half)
        if not _clear(mx, my, MEADOW_MARGIN):
            continue
        if any((s[0]-mx)*(s[0]-mx) + (s[1]-my)*(s[1]-my) < MEADOW_SEP*MEADOW_SEP
               for s in meadow_seeds):
            continue
        meadow_seeds.append([float(mx), float(my)])
    for seed in meadow_seeds:
        shape = _pick_shape()
        major, minor = _blob_axes(random.uniform(55, 130), shape)
        orient = random.random() * math.pi * 2
        n_green = random.randint(4, 12)
        g_sep = 28
        greens = []
        ga = 0
        gmax = n_green * 40
        while len(greens) < n_green and ga < gmax:
            ga += 1
            gx, gy = _sample_blob(seed[0], seed[1], major, minor, orient, shape, 0.55)
            if not _clear(gx, gy, 4):
                continue
            if any((g[0]-gx)*(g[0]-gx) + (g[1]-gy)*(g[1]-gy) < g_sep*g_sep
                   for g in greens):
                continue
            greens.append([gx, gy])
        # drop undersized clumps so we never leave a few lonely squares
        if len(greens) < 3:
            continue
        for gc in greens:
            vegetation.append(MapObject(
                'terrain_green', 'terrain_green', gc, random.randint(0, 359), []))

    # --- 2. Forest patches (main "more vegetation" mechanism) ---
    # Each patch picks a density profile and a blob shape so the map reads as
    # mixed open woodland / medium stands / thick forest, not uniform circles.
    NUM_PATCHES = random.randint(90, 190)
    PATCH_SEP = 590
    PATCH_MARGIN = 210
    # density: (tree_count_scale, tree_sep, green_fill_scale, understory_chance)
    DENSITY_PROFILES = {
        'sparse': (0.45, 110, 0.22, 0.18),
        'medium': (0.85, 82, 0.48, 0.38),
        'dense':  (1.35, 62, 0.78, 0.58),
    }
    DENSITY_WEIGHTS = [0.30, 0.45, 0.25]  # sparse, medium, dense

    patches = []
    attempts = 0
    max_att = NUM_PATCHES * 45
    while len(patches) < NUM_PATCHES and attempts < max_att:
        attempts += 1
        px = random.randint(-half, half)
        py = random.randint(-half, half)
        if not _clear(px, py, PATCH_MARGIN):
            continue
        if any((p[0]-px)*(p[0]-px) + (p[1]-py)*(p[1]-py) < PATCH_SEP*PATCH_SEP for p in patches):
            continue
        patches.append([px, py])

    for seed in patches:
        dens_name = random.choices(
            ['sparse', 'medium', 'dense'], weights=DENSITY_WEIGHTS)[0]
        t_scale, t_sep, g_scale, under_p = DENSITY_PROFILES[dens_name]
        shape = _pick_shape()
        orient = random.random() * math.pi * 2
        size = random.uniform(340, 700)
        major, minor = _blob_axes(size, shape)

        # trees
        area_scale = (major * minor) / (520.0 * 520.0)
        n_trees = max(2, int(random.randint(6, 22) * t_scale * math.sqrt(max(0.25, area_scale))))
        t_margin = 30
        trees = []
        ta = 0
        tmax = n_trees * 70
        while len(trees) < n_trees and ta < tmax:
            ta += 1
            # trees slightly more center-weighted in dense stands, more spread in sparse
            edge = 0.78 if dens_name == 'sparse' else (0.62 if dens_name == 'medium' else 0.48)
            tx, ty = _sample_blob(seed[0], seed[1], major, minor, orient, shape, edge)
            if not _clear(tx, ty, t_margin):
                continue
            if any((tt[0]-tx)*(tt[0]-tx) + (tt[1]-ty)*(tt[1]-ty) < t_sep*t_sep for tt in trees):
                continue
            trees.append([tx, ty])
        for tc in trees:
            rot = random.randint(0, 359)
            vegetation.append(MapObject('pinus_sylvestris', 'pinus_sylvestris', tc, rot, []))
            # small under-tree clump (never a single square)
            if random.random() < under_p:
                for _ in range(random.randint(3, 6)):
                    ox = random.randint(-30, 30)
                    oy = random.randint(-30, 30)
                    vegetation.append(MapObject(
                        'terrain_green', 'terrain_green',
                        [tc[0]+ox, tc[1]+oy], random.randint(0, 359), []))

        # ground cover fill inside the same blob (main green carpet)
        g_major = major + random.uniform(60, 160)
        g_minor = minor + random.uniform(40, 120)
        target_g = int((g_major / 82.0) * (g_minor / 82.0) * g_scale)
        g_margin = 2
        added = 0
        tries = 0
        max_tries = max(30, target_g * 4)
        while added < target_g and tries < max_tries:
            tries += 1
            ex, ey = _sample_blob(seed[0], seed[1], g_major, g_minor, orient, shape, 0.5)
            if _clear(ex, ey, g_margin):
                vegetation.append(MapObject(
                    'terrain_green', 'terrain_green',
                    [float(ex), float(ey)], random.randint(0, 359), []))
                added += 1

        # lobe / satellite sub-clumps: push along the long axis to reinforce
        # kidney/oval silhouettes (and break remaining circular feel)
        if dens_name != 'sparse' and random.random() < 0.70:
            nsubs = 1 if dens_name == 'medium' else random.randint(1, 2)
            for _ in range(nsubs):
                # prefer offset along major axis with some lateral noise
                along = random.uniform(0.35, 0.75) * major * random.choice([-1.0, 1.0])
                across = random.gauss(0, minor * 0.28)
                ca = math.cos(orient)
                sa = math.sin(orient)
                sub_c = [
                    seed[0] + along * ca - across * sa,
                    seed[1] + along * sa + across * ca,
                ]
                sub_shape = random.choice(['oval', 'kidney', shape])
                sub_major, sub_minor = _blob_axes(
                    random.uniform(0.35, 0.65) * major, sub_shape)
                sub_orient = orient + random.uniform(-0.55, 0.55)
                sub_target = int((sub_major / 88.0) * (sub_minor / 88.0) * g_scale * 0.85)
                st = 0
                smax = max(15, sub_target * 3)
                placed = 0
                while placed < sub_target and st < smax:
                    st += 1
                    ex, ey = _sample_blob(
                        sub_c[0], sub_c[1], sub_major, sub_minor,
                        sub_orient, sub_shape, 0.5)
                    if _clear(ex, ey, 2):
                        vegetation.append(MapObject(
                            'terrain_green', 'terrain_green',
                            [float(ex), float(ey)], random.randint(0, 359), []))
                        placed += 1

    # --- 3. Scattered trees (open country, light understory) ---
    SCAT_TARGET = random.randint(90, 240)
    SCAT_SEP = 225
    SCAT_MARGIN = 48
    scats = []
    sa = 0
    smax = SCAT_TARGET * 55
    while len(scats) < SCAT_TARGET and sa < smax:
        sa += 1
        sx = random.randint(-half, half)
        sy = random.randint(-half, half)
        if not _clear(sx, sy, SCAT_MARGIN):
            continue
        if any((ss[0]-sx)*(ss[0]-sx) + (ss[1]-sy)*(ss[1]-sy) < SCAT_SEP*SCAT_SEP for ss in scats):
            continue
        scats.append([sx, sy])
    for sc in scats:
        rot = random.randint(0, 359)
        vegetation.append(MapObject('pinus_sylvestris', 'pinus_sylvestris', sc, rot, []))
        # small under-tree clump (never a single square)
        if random.random() < 0.28:
            for _ in range(random.randint(3, 5)):
                vegetation.append(MapObject(
                    'terrain_green', 'terrain_green',
                    [sc[0]+random.randint(-28, 28), sc[1]+random.randint(-28, 28)],
                    random.randint(0, 359), []))

    return vegetation



