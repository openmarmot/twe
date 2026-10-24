'''
repo : https://github.com/openmarmot/twe

notes :
this class contains code for the main game menu
custom scenario rolls a quick-battle list, then the player edits counts



'''

#import built in modules
import random
import os

#import custom packages
import engine.world_builder
import engine.battlegroup_generator
import engine.math_2d


#global variables


# ------------------------------------------------------------------------------
def wrap_menu_text(text, width=58):
    '''word wrap a block of text for the menu text_queue'''
    lines = []
    if text is None:
        return lines
    paragraphs = str(text).split('\n')
    for para in paragraphs:
        para = para.strip()
        if para == '':
            lines.append('')
            continue
        current = ''
        for word in para.split():
            if current == '':
                current = word
            elif len(current) + 1 + len(word) <= width:
                current = current + ' ' + word
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


# rows on one custom-scenario page. up and down move the selection.
# left and right change page.
CUSTOM_PAGE_SIZE = 8


# ------------------------------------------------------------------------------
def format_squad_amount_header(cost_label):
    '''column titles aligned with format_squad_amount_line'''
    return (
        '  # x'
        + '    '
        + str(cost_label).rjust(6)
        + '  '
        + 'type'.ljust(22)
        + '  squad'
    )


# ------------------------------------------------------------------------------
def format_squad_amount_line(selected, slot, count, cost, squad_type, name):
    '''one custom-scenario row. the point figure sits on the left.'''
    if selected:
        marker = '>'
    else:
        marker = ' '
    type_text = str(squad_type)
    if len(type_text) > 22:
        type_text = type_text[:22]
    return (
        marker
        + str(slot)
        + '  x'
        + str(count).ljust(4)
        + str(cost).rjust(6)
        + '  '
        + type_text.ljust(22)
        + '  '
        + str(name)
    )


class GameMenu():
    ''' in game menu '''

    #---------------------------------------------------------------------------
    def __init__(self,graphics_engine):
        # called/created by world.__init__

        self.active_menu='start' # which menu type (debug/weapon/vehicle/etc)
        self.menu_state='none' # where you are in the menu

        self.text_queue=[]

        self.graphics_engine=graphics_engine

        # used for multiple page layouts
        self.current_page=0

        #
        self.player_spawn_faction=""

        # index into world_builder.scenario_data for the Scenario menu
        self.scenario_index=0

        # custom scenario. reset again each time that menu is opened
        self.custom_year = 1944
        self.custom_points = 5000
        self.custom_side = 'german'
        self.custom_order = {'german': [], 'soviet': []}
        self.custom_counts = {'german': {}, 'soviet': {}}
        self.custom_budget = {'german': 5000, 'soviet': 7500}
        self.custom_index = {'german': 0, 'soviet': 0}
        self.custom_add_index = 0
        self.custom_catalog = []
        self.custom_notice = ''

        # get the initial text going
        self.start_menu('none')
    #---------------------------------------------------------------------------
    def handle_input(self,key):
        '''handle input from the user'''
        # called by graphics_2d_pygame when there is a suitable key press
        # key is a string corresponding to the actual key being pressed

        if key=='esc':
            self.deactivate_menu()
            self.change_menu('start')

        if self.active_menu=='start':
            self.start_menu(key)
        elif self.active_menu=='load_save':
            self.load_save_menu(key)
        elif self.active_menu=='scenario':
            self.scenario_menu(key)
        elif self.active_menu=='custom_scenario':
            self.custom_scenario_menu(key)

        else:
            print('Error : active menu not recognized ',self.active_menu)

    #---------------------------------------------------------------------------
    def change_menu(self,menu_name):
        '''change the menu to the specified menu'''
        self.menu_state='none'
        self.current_page=0
        # clear this just in case as it is rather inconsistently done
        self.text_queue=[]
        self.active_menu=menu_name
        self.handle_input(None)

    #---------------------------------------------------------------------------
    def deactivate_menu(self):
        '''deactivate the menu'''
        self.active_menu='none'
        self.menu_state='none'
        self.text_queue=[]

    #---------------------------------------------------------------------------
    def load_save_menu(self, key):
        '''load save menu'''
        if self.menu_state == 'none':
            # self.graphics_engine.world.is_paused = False
            self.text_queue = []
            self.text_queue.append('Load a save game')
            self.text_queue.append('--- List of Save files ---')

            save_file_names = []

            # Add a list of all file names in ./saves to save_file_names
            save_folder = './saves'
            if os.path.exists(save_folder):
                save_file_names = [f for f in os.listdir(save_folder) if os.path.isfile(os.path.join(save_folder, f)) and f.endswith('.sqlite')]

            if len(save_file_names)==0:
                self.text_queue.append('No Save Files Exist')
                self.text_queue.append('Press [Esc] to return to the main menu')
            else:

                # Dynamically print a key and the corresponding save file name from save_file_names
                files_per_page = 9
                total_pages = (len(save_file_names) + files_per_page - 1) // files_per_page

                start_index = self.current_page * files_per_page
                end_index = min(start_index + files_per_page, len(save_file_names))

                for index, file_name in enumerate(save_file_names[start_index:end_index]):
                    self.text_queue.append(f"{index + 1} - {file_name}")

                if len(save_file_names) > files_per_page:
                    if self.current_page < total_pages - 1:
                        self.text_queue.append("[+] - Next page")
                    if self.current_page > 0:
                        self.text_queue.append("[-] - Previous page")


                # Handle the key selection for more than 10 save files
                if key is not None:
                    if key.isdigit():
                        key_index = int(key) - 1
                        if 0 <= key_index < len(save_file_names[start_index:end_index]):
                            selected_file = save_file_names[start_index + key_index]
                            self.graphics_engine.mode=2
                            self.graphics_engine.strategic_map.load_campaign_from_save('saves/'+selected_file)
                            self.deactivate_menu()
                    elif key == '+' and self.current_page < total_pages - 1:
                        self.current_page += 1
                        self.load_save_menu('')
                    elif key == '-' and self.current_page > 0:
                        self.current_page -= 1
                        self.load_save_menu('')

    #---------------------------------------------------------------------------
    def start_menu(self, key):
        '''start menu'''
        if self.menu_state=='none':
            #self.graphics_engine.world.is_paused=False
            self.text_queue=[]
            self.text_queue.append('TWE: To Whatever End')
            self.text_queue.append('---------------')
            self.text_queue.append('')
            self.text_queue.append('1 - New Campaign (preview)')
            self.text_queue.append('2 - Load Campaign (preview)')
            self.text_queue.append('3 - Quick Battle (choose this)')
            self.text_queue.append('4 - Scenario')
            self.text_queue.append('5 - Custom Scenario')
            self.text_queue.append('6 - Exit')

            if key=='1':
                self.graphics_engine.mode=2
                self.graphics_engine.strategic_map.start_new_campaign()
                self.deactivate_menu()
            elif key=='2':
                self.change_menu('load_save')
            elif key=='3':
                self.menu_state='faction_select'
                key='none'
            elif key=='4':
                self.change_menu('scenario')
            elif key=='5':
                self.change_menu('custom_scenario')
            elif key=='6':
                print('----------------------')
                print('Good Bye!')
                self.graphics_engine.quit=True

        if self.menu_state=='faction_select':
            self.text_queue=[]
            self.text_queue.append('TWE: To Whatever End')
            self.text_queue.append('---------------')
            self.text_queue.append('Pick a Faction')
            self.text_queue.append('1 - American (not implemented)')
            self.text_queue.append('2 - German')
            self.text_queue.append('3 - Soviet')
            self.text_queue.append('4 - Civilian/Neutral')

            # note 1 is missing as americans are not implemented
            if key in ['2','3','4']:
                if key=='1':
                    self.player_spawn_faction='american'
                elif key=='2':
                    self.player_spawn_faction='german'
                elif key=='3':
                    self.player_spawn_faction='soviet'
                elif key=='4':
                    self.player_spawn_faction='civilian'

                self.menu_state='battle_select'
                key='none'

        if self.menu_state=='battle_select':
            self.text_queue=[]
            self.text_queue.append('TWE: To Whatever End')
            self.text_queue.append('---------------')
            self.text_queue.append('Pick a Quick Battle Scenario')
            self.text_queue.append('Note - balance varies wildly with code updates.')

            self.text_queue.append('1 - 5k point random battle ')
            self.text_queue.append('2 - 10k point random battle')
            self.text_queue.append('3 - 20k point random battle')
            self.text_queue.append('4 - Reserved for testing, content will vary')
            self.text_queue.append('5 - 100v100 tank battle for benchmarking')

            if key in ['1','2','3','4','5']:
                self.deactivate_menu()
                self.graphics_engine.load_quick_battle(self.player_spawn_faction,key)

    #---------------------------------------------------------------------------
    def scenario_menu(self, key):
        '''browse and start a predefined scenario'''

        scenarios = engine.world_builder.scenario_data
        self.text_queue = []
        self.text_queue.append('TWE: To Whatever End')
        self.text_queue.append('---------------')

        if not scenarios:
            self.text_queue.append('No scenarios found')
            self.text_queue.append('Press [Esc] to return to the main menu')
            return

        if self.scenario_index >= len(scenarios) or self.scenario_index < 0:
            self.scenario_index = 0

        # next / previous. wrap around so a long list stays usable
        if key in ['4', '+']:
            self.scenario_index = (self.scenario_index + 1) % len(scenarios)
            key = None
        elif key in ['5', '-']:
            self.scenario_index = (self.scenario_index - 1) % len(scenarios)
            key = None

        s = scenarios[self.scenario_index]
        total = len(scenarios)
        attacking = str(s.get('attacking_faction', 'none'))
        defending = str(s.get('defending_faction', 'none'))
        year = s.get('year', '')
        map_parts = []
        for part in str(s.get('map_areas', '')).split(','):
            part = part.strip().replace('_', ' ')
            if part:
                map_parts.append(part.title())
        map_areas = ', '.join(map_parts)

        self.text_queue.append(
            'Scenario  ' + str(self.scenario_index + 1) + ' / ' + str(total)
        )
        self.text_queue.append(str(s.get('name', 'Unnamed')))
        self.text_queue.append('Year ' + str(year))
        if defending in ['none', 'contested']:
            self.text_queue.append(
                'Meeting engagement  (' + defending + ')'
            )
        else:
            self.text_queue.append(
                attacking.capitalize()
                + ' attacking  /  '
                + defending.capitalize()
                + ' defending'
            )
        self.text_queue.append('Map: ' + map_areas)
        self.text_queue.append('---------------')
        for line in wrap_menu_text(s.get('description', '')):
            self.text_queue.append(line)
        self.text_queue.append('---------------')
        self.text_queue.append('1 - Play as German')
        self.text_queue.append('2 - Play as Soviet')
        self.text_queue.append('3 - Play as Civilian/Neutral')
        self.text_queue.append('4 - Next scenario')
        self.text_queue.append('5 - Previous scenario')

        if key == '1':
            faction = 'german'
        elif key == '2':
            faction = 'soviet'
        elif key == '3':
            faction = 'civilian'
        else:
            faction = None

        if faction is not None:
            self.player_spawn_faction = faction
            self.deactivate_menu()
            self.graphics_engine.load_scenario(faction, s)

    #---------------------------------------------------------------------------
    def custom_scenario_menu(self, key):
        '''pick a year and points, edit the rolled squad lists, then start'''

        # change_menu sets menu_state to none before the first draw
        if self.menu_state == 'none':
            self.custom_scenario_reset()
            self.menu_state = 'setup'

        if self.menu_state == 'setup':
            self.custom_scenario_handle_setup(key)
        elif self.menu_state == 'edit':
            self.custom_scenario_handle_edit(key)
        elif self.menu_state == 'add':
            self.custom_scenario_handle_add(key)
        elif self.menu_state == 'confirm_roll':
            self.custom_scenario_handle_confirm_roll(key)
        elif self.menu_state == 'play_as':
            self.custom_scenario_handle_play_as(key)

        # starting the battle deactivates the menu. do not draw over that.
        if self.active_menu != 'custom_scenario':
            return

        if self.menu_state == 'setup':
            self.custom_scenario_draw_setup()
        elif self.menu_state == 'edit':
            self.custom_scenario_draw_edit()
        elif self.menu_state == 'add':
            self.custom_scenario_draw_add()
        elif self.menu_state == 'confirm_roll':
            self.custom_scenario_draw_confirm_roll()
        elif self.menu_state == 'play_as':
            self.custom_scenario_draw_play_as()

    #---------------------------------------------------------------------------
    def custom_scenario_reset(self):
        '''default year, points, and empty lists'''
        self.custom_year = 1944
        self.custom_points = 5000
        self.custom_side = 'german'
        self.custom_order = {'german': [], 'soviet': []}
        self.custom_counts = {'german': {}, 'soviet': {}}
        self.custom_budget = {'german': 5000, 'soviet': 7500}
        self.custom_index = {'german': 0, 'soviet': 0}
        self.custom_add_index = 0
        self.custom_catalog = []
        self.custom_notice = ''

    #---------------------------------------------------------------------------
    def custom_scenario_set_points(self, points):
        '''keep the budget on a 500 point step between 500 and 20000'''
        try:
            points = int(points)
        except (TypeError, ValueError):
            return
        if points < 500:
            points = 500
        if points > 20000:
            points = 20000
        self.custom_points = int(points / 500) * 500

    #---------------------------------------------------------------------------
    def custom_scenario_apply_roll(self, result):
        '''store a fresh roll for both sides'''
        for side in ('german', 'soviet'):
            order, counts = engine.world_builder.squad_counts_from_names(
                result[side]
            )
            self.custom_order[side] = order
            self.custom_counts[side] = counts
            self.custom_index[side] = 0
        self.custom_budget['german'] = result['german_budget']
        self.custom_budget['soviet'] = result['soviet_budget']
        self.custom_year = result['year']
        self.custom_side = 'german'

    #---------------------------------------------------------------------------
    def custom_scenario_side_total_line(self, side, mark=True):
        '''live point total for one side, next to the budget it was rolled from'''
        total = engine.world_builder.squad_force_cost(
            self.custom_order[side], self.custom_counts[side]
        )
        if side == 'german':
            label = 'German'
        else:
            label = 'Soviet'
        if mark and side == self.custom_side:
            marker = '>'
        else:
            marker = ' '
        budget = self.custom_budget.get(side, 0)
        return (
            marker
            + ' '
            + label
            + '  '
            + str(total)
            + ' pts'
            + '   (budget '
            + str(budget)
            + ')'
        )

    #---------------------------------------------------------------------------
    def custom_scenario_clamp_index(self):
        '''keep the selected row inside the side that is on screen'''
        side = self.custom_side
        order = self.custom_order[side]
        index = self.custom_index.get(side, 0)
        if not order:
            self.custom_index[side] = 0
            return
        if index >= len(order):
            index = len(order) - 1
        if index < 0:
            index = 0
        self.custom_index[side] = index

    #---------------------------------------------------------------------------
    def custom_scenario_selected_name(self):
        '''squad name on the selected row, or None when that side is empty'''
        order = self.custom_order[self.custom_side]
        if not order:
            return None
        self.custom_scenario_clamp_index()
        return order[self.custom_index[self.custom_side]]

    #---------------------------------------------------------------------------
    def custom_scenario_page(self, length, index):
        '''page, page count, and the slice of rows that fit on one screen'''
        page_size = CUSTOM_PAGE_SIZE
        if length <= 0:
            return 0, 1, 0, 0
        if index < 0:
            index = 0
        if index >= length:
            index = length - 1
        page = int(index / page_size)
        pages = int((length + page_size - 1) / page_size)
        start = page * page_size
        end = start + page_size
        if end > length:
            end = length
        return page, pages, start, end

    #---------------------------------------------------------------------------
    def custom_scenario_shift_index(self, index, length, key):
        '''move a list cursor. up and down by one, left and right by a page.'''
        if length <= 0:
            return 0
        if index < 0:
            index = 0
        if index >= length:
            index = length - 1
        if key == 'up':
            if index > 0:
                index -= 1
        elif key == 'down':
            if index < length - 1:
                index += 1
        elif key in ['left', 'right']:
            page, pages, start, _end = self.custom_scenario_page(length, index)
            offset = index - start
            if key == 'left':
                new_page = page - 1
            else:
                new_page = page + 1
            if new_page < 0 or new_page >= pages:
                return index
            index = new_page * CUSTOM_PAGE_SIZE + offset
            if index >= length:
                index = length - 1
        return index

    #---------------------------------------------------------------------------
    def custom_scenario_related_count(self, name):
        '''copies of this squad already fielded, including camo skins'''
        counts = self.custom_counts[self.custom_side]
        groups = engine.battlegroup_generator.get_camo_groups(
            engine.world_builder.squad_data
        )
        related = engine.battlegroup_generator.related_squad_names(name, groups)
        total = 0
        for related_name in related:
            total += counts.get(related_name, 0)
        return total

    #---------------------------------------------------------------------------
    def custom_scenario_give_squad(self, name, amount):
        '''add or remove copies of one squad on the side being edited'''
        if name is None or amount == 0:
            return
        side = self.custom_side
        order = self.custom_order[side]
        counts = self.custom_counts[side]
        if name not in counts:
            if amount < 0:
                return
            order.append(name)
            counts[name] = 0
        counts[name] += amount
        if counts[name] <= 0:
            del counts[name]
            if name in order:
                order.remove(name)
            self.custom_scenario_clamp_index()
        else:
            self.custom_index[side] = order.index(name)

    #---------------------------------------------------------------------------
    def custom_scenario_open_add(self):
        '''catalog of squads this side can field in the chosen year'''
        self.custom_catalog = engine.world_builder.custom_scenario_squad_choices(
            self.custom_side, self.custom_year
        )
        self.custom_add_index = 0
        self.menu_state = 'add'

    #---------------------------------------------------------------------------
    def custom_scenario_choice_line(self, key_label, text, selected):
        '''a setup-screen choice. the current one is marked'''
        line = key_label + ' - ' + text
        if selected:
            line = line + '   <'
        return line

    #---------------------------------------------------------------------------
    def custom_scenario_draw_setup(self):
        '''year and point budget'''
        german_budget, soviet_budget = engine.world_builder.custom_scenario_budgets(
            self.custom_points
        )
        self.text_queue = []
        self.text_queue.append('TWE: To Whatever End')
        self.text_queue.append('Custom Scenario')
        self.text_queue.append('---------------')
        self.text_queue.append('Pick a year and a point budget.')
        self.text_queue.append('Each side gets a squad list rolled')
        self.text_queue.append('the same way as a quick battle.')
        self.text_queue.append('Soviets get 50% more points.')
        self.text_queue.append('You can change the squad counts next.')
        self.text_queue.append('---------------')
        self.text_queue.append('Year')
        self.text_queue.append(self.custom_scenario_choice_line(
            '1', '1944', self.custom_year == 1944
        ))
        self.text_queue.append(self.custom_scenario_choice_line(
            '2', '1945', self.custom_year == 1945
        ))
        self.text_queue.append('---------------')
        self.text_queue.append('Points  ' + str(self.custom_points))
        self.text_queue.append(self.custom_scenario_choice_line(
            '3', '2500', self.custom_points == 2500
        ))
        self.text_queue.append(self.custom_scenario_choice_line(
            '4', '5000', self.custom_points == 5000
        ))
        self.text_queue.append(self.custom_scenario_choice_line(
            '5', '10000', self.custom_points == 10000
        ))
        self.text_queue.append('+ - Add 500 points')
        self.text_queue.append('- - Subtract 500 points')
        self.text_queue.append('500 to 20000')
        self.text_queue.append('---------------')
        self.text_queue.append('German budget  ' + str(german_budget))
        self.text_queue.append('Soviet budget  ' + str(soviet_budget))
        self.text_queue.append('---------------')
        self.text_queue.append('6 - Generate forces')
        self.text_queue.append('Esc - Main menu')

    #---------------------------------------------------------------------------
    def custom_scenario_draw_edit(self):
        '''squad counts for the side being edited, and both point totals'''
        self.custom_scenario_clamp_index()
        side = self.custom_side
        order = self.custom_order[side]
        counts = self.custom_counts[side]
        index = self.custom_index[side]
        page, pages, start, end = self.custom_scenario_page(len(order), index)

        units = 0
        for squad_name in order:
            units += counts.get(squad_name, 0)
        if side == 'german':
            side_label = 'German'
        else:
            side_label = 'Soviet'

        self.text_queue = []
        self.text_queue.append('TWE: To Whatever End')
        self.text_queue.append('Custom Scenario    Year ' + str(self.custom_year))
        self.text_queue.append(self.custom_scenario_side_total_line('german'))
        self.text_queue.append(self.custom_scenario_side_total_line('soviet'))
        self.text_queue.append('---------------')
        self.text_queue.append(
            side_label
            + ' list    '
            + str(units)
            + ' squads    page '
            + str(page + 1)
            + ' / '
            + str(pages)
        )
        if not order:
            self.text_queue.append('No squads on this side yet')
        else:
            self.text_queue.append(format_squad_amount_header('total'))
            slot = 1
            for row_index in range(start, end):
                name = order[row_index]
                count = counts.get(name, 0)
                info = engine.world_builder.squad_data.get(name, {})
                line_cost = engine.world_builder.squad_unit_cost(name) * count
                self.text_queue.append(format_squad_amount_line(
                    row_index == index,
                    slot,
                    count,
                    line_cost,
                    info.get('type', ''),
                    name,
                ))
                slot += 1

        self.text_queue.append('---------------')
        selected = self.custom_scenario_selected_name()
        if selected is not None:
            each = engine.world_builder.squad_unit_cost(selected)
            self.text_queue.append(
                'Selected  ' + selected + '    ' + str(each) + ' pts each'
            )
        self.text_queue.append('Up / Down - Select a squad')
        self.text_queue.append('+ - Add one of the selected squad')
        self.text_queue.append('- - Remove one of the selected squad')
        self.text_queue.append('[ - German list')
        self.text_queue.append('] - Soviet list')
        self.text_queue.append('Left / Right - Change page')
        self.text_queue.append('9 - Add a squad that is not listed')
        self.text_queue.append('r - Roll both sides again')
        self.text_queue.append('0 - Start battle')
        self.text_queue.append('Esc - Main menu')
        if self.custom_notice:
            self.text_queue.append(self.custom_notice)

    #---------------------------------------------------------------------------
    def custom_scenario_draw_add(self):
        '''every squad this side can field. adding one updates the point total.'''
        length = len(self.custom_catalog)
        if length <= 0:
            self.custom_add_index = 0
        elif self.custom_add_index >= length:
            self.custom_add_index = length - 1
        elif self.custom_add_index < 0:
            self.custom_add_index = 0
        page, pages, start, end = self.custom_scenario_page(
            length, self.custom_add_index
        )

        if self.custom_side == 'german':
            side_label = 'German'
        else:
            side_label = 'Soviet'

        self.text_queue = []
        self.text_queue.append('TWE: To Whatever End')
        self.text_queue.append(
            'Add a ' + side_label + ' squad    ' + str(self.custom_year)
        )
        self.text_queue.append(self.custom_scenario_side_total_line('german'))
        self.text_queue.append(self.custom_scenario_side_total_line('soviet'))
        self.text_queue.append('Squads this side can field in this year.')
        self.text_queue.append('The count includes a camo skin of that squad.')
        self.text_queue.append(
            'page '
            + str(page + 1)
            + ' / '
            + str(pages)
        )
        if length == 0:
            self.text_queue.append('No squads for this side')
        else:
            self.text_queue.append(format_squad_amount_header('each'))
            slot = 1
            for row_index in range(start, end):
                name = self.custom_catalog[row_index]
                info = engine.world_builder.squad_data.get(name, {})
                self.text_queue.append(format_squad_amount_line(
                    row_index == self.custom_add_index,
                    slot,
                    self.custom_scenario_related_count(name),
                    engine.world_builder.squad_unit_cost(name),
                    info.get('type', ''),
                    name,
                ))
                slot += 1
        self.text_queue.append('---------------')
        if length > 0:
            selected = self.custom_catalog[self.custom_add_index]
            each = engine.world_builder.squad_unit_cost(selected)
            self.text_queue.append(
                'Selected  ' + selected + '    ' + str(each) + ' pts each'
            )
        self.text_queue.append('Up / Down - Select a squad')
        self.text_queue.append('+ - Add one of the selected squad')
        self.text_queue.append('- - Remove one of the selected squad')
        self.text_queue.append('[ - German squads')
        self.text_queue.append('] - Soviet squads')
        self.text_queue.append('Left / Right - Change page')
        self.text_queue.append('0 - Back to the lists')
        self.text_queue.append('Esc - Main menu')

    #---------------------------------------------------------------------------
    def custom_scenario_draw_confirm_roll(self):
        '''confirm replacing both edited lists'''
        self.text_queue = []
        self.text_queue.append('TWE: To Whatever End')
        self.text_queue.append('Custom Scenario')
        self.text_queue.append('---------------')
        self.text_queue.append('Roll again?')
        self.text_queue.append('This replaces the German and Soviet lists.')
        self.text_queue.append('Year ' + str(self.custom_year))
        self.text_queue.append(
            'German budget  ' + str(self.custom_budget.get('german', 0))
        )
        self.text_queue.append(
            'Soviet budget  ' + str(self.custom_budget.get('soviet', 0))
        )
        self.text_queue.append('---------------')
        self.text_queue.append('1 - Roll again')
        self.text_queue.append('0 - Keep the current lists')

    #---------------------------------------------------------------------------
    def custom_scenario_draw_play_as(self):
        '''who the player spawns as'''
        self.text_queue = []
        self.text_queue.append('TWE: To Whatever End')
        self.text_queue.append('Custom Scenario')
        self.text_queue.append('Year ' + str(self.custom_year))
        self.text_queue.append(
            self.custom_scenario_side_total_line('german', False)
        )
        self.text_queue.append(
            self.custom_scenario_side_total_line('soviet', False)
        )
        self.text_queue.append('---------------')
        self.text_queue.append('Pick who you play')
        self.text_queue.append('1 - German')
        self.text_queue.append('2 - Soviet')
        self.text_queue.append('3 - Civilian/Neutral')
        self.text_queue.append('0 - Back')

    #---------------------------------------------------------------------------
    def custom_scenario_handle_setup(self, key):
        '''year, budget, then roll'''
        if key is None or key == 'none':
            return
        if key == '1':
            self.custom_year = 1944
        elif key == '2':
            self.custom_year = 1945
        elif key == '3':
            self.custom_scenario_set_points(2500)
        elif key == '4':
            self.custom_scenario_set_points(5000)
        elif key == '5':
            self.custom_scenario_set_points(10000)
        elif key == '+':
            self.custom_scenario_set_points(self.custom_points + 500)
        elif key == '-':
            self.custom_scenario_set_points(self.custom_points - 500)
        elif key == '6':
            result = engine.world_builder.generate_custom_scenario_forces(
                self.custom_points, self.custom_year
            )
            self.custom_scenario_apply_roll(result)
            self.custom_notice = ''
            self.menu_state = 'edit'

    #---------------------------------------------------------------------------
    def custom_scenario_handle_edit(self, key):
        '''change counts, switch side, or leave for add / roll / start'''
        if key is None or key == 'none':
            return
        self.custom_notice = ''
        self.custom_scenario_clamp_index()
        order = self.custom_order[self.custom_side]
        if key in ['up', 'down', 'left', 'right']:
            self.custom_index[self.custom_side] = self.custom_scenario_shift_index(
                self.custom_index[self.custom_side], len(order), key
            )
        elif key == '+':
            self.custom_scenario_give_squad(
                self.custom_scenario_selected_name(), 1
            )
        elif key == '-':
            self.custom_scenario_give_squad(
                self.custom_scenario_selected_name(), -1
            )
        elif key == '[':
            self.custom_side = 'german'
        elif key == ']':
            self.custom_side = 'soviet'
        elif key == '9':
            self.custom_scenario_open_add()
        elif key == 'r':
            self.menu_state = 'confirm_roll'
        elif key == '0':
            german_units = sum(self.custom_counts['german'].values())
            soviet_units = sum(self.custom_counts['soviet'].values())
            if german_units <= 0 and soviet_units <= 0:
                self.custom_notice = 'Add at least one squad before starting'
            else:
                self.menu_state = 'play_as'

    #---------------------------------------------------------------------------
    def custom_scenario_handle_add(self, key):
        '''add one copy of a catalog squad. the point total updates on the draw.'''
        if key is None or key == 'none':
            return
        length = len(self.custom_catalog)
        if key in ['up', 'down', 'left', 'right']:
            self.custom_add_index = self.custom_scenario_shift_index(
                self.custom_add_index, length, key
            )
        elif key == '+' and length > 0:
            self.custom_scenario_give_squad(
                self.custom_catalog[self.custom_add_index], 1
            )
        elif key == '-' and length > 0:
            self.custom_scenario_give_squad(
                self.custom_catalog[self.custom_add_index], -1
            )
        elif key == '[':
            self.custom_side = 'german'
            self.custom_scenario_open_add()
        elif key == ']':
            self.custom_side = 'soviet'
            self.custom_scenario_open_add()
        elif key == '0':
            self.menu_state = 'edit'

    #---------------------------------------------------------------------------
    def custom_scenario_handle_confirm_roll(self, key):
        '''replace both lists, or go back'''
        if key is None or key == 'none':
            return
        if key == '1':
            result = engine.world_builder.generate_custom_scenario_forces(
                self.custom_points, self.custom_year
            )
            self.custom_scenario_apply_roll(result)
            self.custom_notice = 'Rolled a new list for both sides'
            self.menu_state = 'edit'
        elif key == '0':
            self.menu_state = 'edit'

    #---------------------------------------------------------------------------
    def custom_scenario_handle_play_as(self, key):
        '''spawn faction, then load the battle from the edited lists'''
        if key is None or key == 'none':
            return
        if key == '0':
            self.menu_state = 'edit'
            return
        if key == '1':
            faction = 'german'
        elif key == '2':
            faction = 'soviet'
        elif key == '3':
            faction = 'civilian'
        else:
            return
        german = engine.world_builder.expand_squad_counts(
            self.custom_order['german'], self.custom_counts['german']
        )
        soviet = engine.world_builder.expand_squad_counts(
            self.custom_order['soviet'], self.custom_counts['soviet']
        )
        year = self.custom_year
        self.deactivate_menu()
        self.graphics_engine.load_custom_scenario(
            faction, year, german, soviet
        )

    #---------------------------------------------------------------------------
    def update(self,time_passed_seconds):
        '''update'''

        # should maybe check if a menu is active first. no need for this to be constantly running
        # make the menu auto close after a period of time

        pass
