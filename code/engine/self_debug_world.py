
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
all the code for self debug of the world state. this can be triggered through the debug menu (~)
'''

#---------------------------------------------------------------------------
def run_object_counts_report(world):
    '''generates a list of objects in world with a count per type'''

    print('------------------------------------')
    print('world object count ')
    print('------------------------------------')
    wo_list={}
    for b in world.wo_objects:
        if b.world_builder_identity in wo_list:
            wo_list[b.world_builder_identity]+=1
        else:
            wo_list[b.world_builder_identity]=1

    for key,value in wo_list.items():
        print(key,'count:',value)
    print('------------------------------------')

#---------------------------------------------------------------------------
def run_wo_objects_check(world):
    '''sanity checks objects in world.wo_objects'''

    print('------------------------------------')
    print('world object count ')
    print('------------------------------------')

    for b in world.wo_objects:
        issues=[]
        if b.in_world is False:
            issues.append(f'{b.name} .in_world is False')
        if b.grid_square is None:
            issues.append(f'{b.name} .grid_square is None')
        else:
            if b not in b.grid_square.wo_objects:
                issues.append(f'{b.name} not in .grid_square.wo_objects')

        if len(issues)>0:
            print('----------')
            for c in issues:
                print(c)
            print('----------')


    print('------------------------------------')

#---------------------------------------------------------------------------
def start(world):
    '''entry point. starts the debug'''

    # for simplicity the debug will print out to console 

    # object counts
    run_object_counts_report(world)

    # object sanity check
    run_wo_objects_check(world)

