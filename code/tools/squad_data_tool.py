'''
repo : https://github.com/openmarmot/twe

notes :
Review tool for the squad_data table in data/data.sqlite.
Reads rows only. It does not spawn objects and it does not write the database.

members is a comma list of world_builder identities. Those are not foreign
keys. The tool reads engine/object_defs so a soldier or vehicle can be shown
with the name and weapons from its definition.

A name ending in " camo" plus an optional number is a skin. Quick battle rolls
the base squad, then picks a skin. This tool still lists the skin rows.

scenario_data stores squads as "Name:count" in german_squads and soviet_squads.
Those counts are shown on the selected squad.

Usage (from the repo root, code/, or code/tools/):
    python3 code/tools/squad_data_tool.py
    python3 squad_data_tool.py /path/to/data.sqlite
'''


# import built in modules
import os
import re
import sqlite3
import sys

# hide the pygame startup line. this has to be set before pygame is imported
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

# import pip packages
import pygame
import pygame.freetype


SCREEN_W = 1440
SCREEN_H = 960
MARGIN = 12
TOP_H = 86
DETAIL_H = 188
HELP_H = 22
BODY_Y = MARGIN + TOP_H + 8
BODY_H = SCREEN_H - BODY_Y - DETAIL_H - HELP_H - 16
DETAIL_Y = BODY_Y + BODY_H + 8
LIST_W = 640
LIST_HEADER_H = 28
TABLE_HEADER_H = 28
LIST_ROW_H = 24
TABLE_ROW_H = 22
MAX_COMPARE = 8

BG = (236, 233, 226)
PANEL = (252, 251, 247)
INK = (42, 40, 36)
MUTED = (110, 104, 96)
LINE = (196, 190, 180)
GRID = (226, 222, 214)
ACCENT = (36, 72, 112)
WARN = (140, 72, 24)
FOCUS = (255, 244, 214)
WHITE = (255, 255, 255)
BAR_1944 = (36, 72, 112)
BAR_1945 = (148, 92, 48)
SOLDIER_COLOR = (86, 108, 86)
VEHICLE_COLOR = (36, 72, 112)

PLOT_COLORS = [
    (31, 119, 180),
    (214, 39, 40),
    (44, 160, 44),
    (230, 120, 14),
    (148, 103, 189),
    (140, 86, 75),
    (190, 70, 150),
    (16, 150, 166),
]

FACTION_COLOR = {
    'german': (64, 88, 62),
    'soviet': (148, 64, 52),
    'civilian': (120, 104, 64),
    'american': (48, 84, 130),
}

# same buckets create_random_battlegroup spends points on
CATEGORY_TYPES = {
    'infantry': ('infantry', 'motorized_infantry', 'mechanized_infantry'),
    'tanks': ('tank',),
    'antitank': ('antitank_vehicle', 'antitank_infantry', 'towed_antitank'),
    'support': ('medic', 'mechanic', 'sniper', 'infantry radio', 'mg'),
    'vehicles': ('fire_support_vehicle', 'towed_antiair', 'recon'),
    'artillery': ('artillery',),
    'command': ('command',),
}

CATEGORY_ORDER = (
    'all',
    'infantry',
    'tanks',
    'antitank',
    'support',
    'vehicles',
    'artillery',
    'command',
    'other',
)

REQUIRED_COLUMNS = (
    'faction',
    'name',
    'type',
    'cost',
    'members',
    'chance_1944',
    'chance_1945',
)

REGISTER_RE = re.compile(r'''@register_object\(\s*["']([^"']+)["']\s*\)''')
NAME_LITERAL_RE = re.compile(r'''z\.name\s*=\s*["']([^"']*)["']''')
LOADOUT_RE = re.compile(
    r'''add_standard_loadout\(\s*\w+\s*,\s*\w+\s*,\s*["']([^"']+)["']\s*\)'''
)
FLAG_RE = re.compile(r'''z\.(is_human|is_vehicle|is_airplane)\s*=\s*True''')


#------------------------------------------------------------------------------
def code_directory():
    '''directory that holds data/ and engine/'''
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(tools_dir)


#------------------------------------------------------------------------------
def database_path():
    '''default data.sqlite next to this script's code directory'''
    return os.path.join(code_directory(), 'data', 'data.sqlite')


#------------------------------------------------------------------------------
def object_defs_directory():
    '''object definition tree. member identities are registered here'''
    return os.path.join(code_directory(), 'engine', 'object_defs')


#------------------------------------------------------------------------------
def prettify_identity(identity):
    '''german_kar98k -> kar98k, kept readable when a definition has no z.name'''
    text = identity
    for prefix in ('german_', 'soviet_', 'civilian_', 'american_'):
        if text.startswith(prefix):
            stripped = text[len(prefix):]
            # "civilian_man" would become "man". keep the faction in that case
            if len(stripped) >= 4:
                text = stripped
            break
    return text.replace('_', ' ')


#------------------------------------------------------------------------------
def camo_base_name(squad_name):
    '''base squad when this name is a camo skin, else None

    same rule as battlegroup_generator.get_camo_base_name
    '''
    marker = ' camo'
    index = squad_name.lower().find(marker)
    if index == -1:
        return None
    after = squad_name[index + len(marker):]
    if after == '' or after.isdigit():
        return squad_name[:index]
    return None


#------------------------------------------------------------------------------
def category_for_type(unit_type):
    '''budget bucket used by the quick battle generator'''
    for category, types in CATEGORY_TYPES.items():
        if unit_type in types:
            return category
    return 'other'


#------------------------------------------------------------------------------
def parse_count_list(text):
    '''parse "Squad:2, Other:1" into (name, count) pairs'''
    entries = []
    if text is None:
        return entries
    for entry in str(text).split(','):
        entry = entry.strip()
        if entry == '':
            continue
        if ':' in entry:
            name, count_text = entry.rsplit(':', 1)
            name = name.strip()
            count_text = count_text.strip()
            try:
                count = int(count_text)
            except ValueError:
                count = 1
        else:
            name = entry
            count = 1
        if name == '':
            continue
        entries.append((name, count))
    return entries


#------------------------------------------------------------------------------
def split_members(text):
    '''comma list used by get_squad_map_objects. empties are dropped'''
    members = []
    if text is None:
        return members
    for part in str(text).split(','):
        identity = part.strip()
        if identity == '':
            continue
        members.append(identity)
    return members


#------------------------------------------------------------------------------
def looks_like_display_name(text):
    '''a builder argument that is a name rather than an object identity'''
    if text is None or text == '':
        return False
    if ' ' in text or '.' in text:
        return True
    for character in text:
        if character.isupper():
            return True
    return False


#------------------------------------------------------------------------------
def spawn_identities(body):
    '''object types passed to spawn_object, in order'''
    found = []
    cursor = 0
    needle = 'spawn_object('
    while True:
        start = body.find(needle, cursor)
        if start == -1:
            return found
        window = body[start + len(needle):start + len(needle) + 240]
        match = re.search(r'''["']([^"']+)["']''', window)
        if match:
            found.append(match.group(1))
        cursor = start + len(needle)


#------------------------------------------------------------------------------
def return_display_name(body):
    '''display name passed into a helper, as in return _create(..., "Sd.Kfz.251/21", ...)'''
    start = body.find('return ')
    if start == -1:
        return None
    window = body[start:start + 500]
    for text in re.findall(r'''["']([^"']+)["']''', window):
        if looks_like_display_name(text):
            return text
    return None


#------------------------------------------------------------------------------
def classify_object(item):
    '''soldier, vehicle, weapon, magazine, or other. from the file path and flags'''
    path = item['file'].replace('\\', '/')
    if '/weapons/magazines/' in path:
        return 'magazine'
    if '/weapons/' in path:
        return 'weapon'
    if '/radio/' in path:
        return 'radio'
    if '/humans/' in path or 'is_human' in item['flags']:
        return 'soldier'
    if '/vehicles/' in path or 'is_vehicle' in item['flags'] or 'is_airplane' in item['flags']:
        return 'vehicle'
    return 'other'


#------------------------------------------------------------------------------
def load_object_index(defs_dir):
    '''map world_builder identity -> display name, kind, gear, skin parent

    static read of the definition files. nothing is imported or spawned.
    '''
    index = {}
    if os.path.isdir(defs_dir) is False:
        print('warning: object definitions not found: ' + defs_dir)
        return index

    for dirpath, _dirnames, filenames in os.walk(defs_dir):
        for filename in filenames:
            if filename.endswith('.py') is False:
                continue
            path = os.path.join(dirpath, filename)
            handle = open(path, 'r', encoding='utf-8', errors='replace')
            text = handle.read()
            handle.close()
            parts = REGISTER_RE.split(text)
            # parts[0] is the preamble. then identity, body, identity, body
            for offset in range(1, len(parts), 2):
                identity = parts[offset]
                body = parts[offset + 1] if offset + 1 < len(parts) else ''
                literal = NAME_LITERAL_RE.search(body)
                spawns = spawn_identities(body)
                parent = None
                for spawned in spawns:
                    if spawned != identity:
                        parent = spawned
                        break
                skin_of = ''
                if parent and 'camo' in identity.lower():
                    skin_of = parent
                item = {
                    'identity': identity,
                    'file': os.path.relpath(path, os.path.dirname(defs_dir)),
                    'literal_name': literal.group(1) if literal else None,
                    'return_name': return_display_name(body),
                    'parent': parent,
                    'skin_of': skin_of,
                    'spawns': spawns,
                    'loadouts': LOADOUT_RE.findall(body),
                    'pistol': 'add_random_pistol_to_inventory' in body,
                    'alternatives': re.search(r'\n[ \t]*else:', body) is not None,
                    'flags': FLAG_RE.findall(body),
                    'display': None,
                    'kind': 'other',
                    'gear': '',
                }
                if identity in index:
                    print('warning: duplicate object identity ' + identity)
                index[identity] = item

    for identity in index:
        resolve_display(index, identity, set())
    for item in index.values():
        item['kind'] = classify_object(item)
    for item in index.values():
        item['gear'] = gear_text(item, index)
    return index


#------------------------------------------------------------------------------
def resolve_display(index, identity, stack):
    '''fill display. a camo wrapper with no name of its own keeps the parent name'''
    item = index.get(identity)
    if item is None:
        return prettify_identity(identity)
    if item['display']:
        return item['display']
    if identity in stack:
        item['display'] = prettify_identity(identity)
        return item['display']
    stack.add(identity)
    if item['literal_name']:
        item['display'] = item['literal_name']
    elif item['return_name']:
        item['display'] = item['return_name']
    elif item['skin_of']:
        item['display'] = resolve_display(index, item['skin_of'], stack)
    else:
        item['display'] = prettify_identity(identity)
    stack.discard(identity)
    return item['display']


#------------------------------------------------------------------------------
def gear_label(token, index):
    '''loadout or weapon identity -> the name stored on that weapon'''
    candidates = (token, token.replace('-', '_'), token.replace('_', '-'))
    for candidate in candidates:
        item = index.get(candidate)
        if item is not None and item['kind'] == 'weapon':
            return item['display'].replace('_', ' ')
    return token.replace('_', ' ')


#------------------------------------------------------------------------------
def gear_text(item, index):
    '''weapons and radios carried by a soldier definition. vehicles stay blank'''
    if item['kind'] != 'soldier':
        return ''
    labels = []
    for token in item['loadouts']:
        if token.startswith('standard_'):
            continue
        label = gear_label(token, index)
        # the loadout id is sometimes more specific than the weapon's z.name
        # (kar98k_schiessbecher's weapon is still named kar98k)
        specific = token.replace('_', ' ').replace('-', ' ')
        if label and label in specific and len(specific) > len(label):
            label = specific
        if label not in labels:
            labels.append(label)
    extras = []
    for identity in item['spawns']:
        other = index.get(identity)
        if other is None:
            continue
        if other['kind'] not in ('weapon', 'radio'):
            continue
        label = other['display']
        if label not in labels and label not in extras:
            extras.append(label)
    if item['pistol'] and 'pistol' not in labels and 'pistol' not in extras:
        extras.append('pistol')
    # german_afv_crew_expert picks stg44 or mp40. both loadouts are in the file.
    if item['alternatives'] and len(labels) > 1:
        text = ' or '.join(labels)
    else:
        text = ', '.join(labels)
    if extras:
        extra_text = ', '.join(extras)
        if text:
            return text + ', ' + extra_text
        return extra_text
    return text


#------------------------------------------------------------------------------
def blank_object(identity):
    '''placeholder when members names an identity with no definition'''
    return {
        'identity': identity,
        'display': identity,
        'kind': 'missing',
        'gear': '',
        'skin_of': '',
        'file': '',
        'registered': False,
    }


#------------------------------------------------------------------------------
def object_info(index, identity):
    '''resolved member, or a missing placeholder'''
    item = index.get(identity)
    if item is None:
        return blank_object(identity)
    return {
        'identity': identity,
        'display': item['display'],
        'kind': item['kind'],
        'gear': item['gear'],
        'skin_of': item['skin_of'],
        'file': item['file'],
        'registered': True,
    }


#------------------------------------------------------------------------------
def member_groups(members, index):
    '''collapse repeats, keep the first-seen order'''
    groups = []
    position = {}
    for identity in members:
        if identity in position:
            groups[position[identity]]['count'] += 1
            continue
        position[identity] = len(groups)
        groups.append({
            'identity': identity,
            'count': 1,
            'info': object_info(index, identity),
        })
    return groups


#------------------------------------------------------------------------------
def skin_root(identity, index):
    '''follow camo wrappers back to the vehicle they reskin'''
    seen = []
    while identity and identity not in seen:
        seen.append(identity)
        item = index.get(identity)
        if item is None:
            break
        parent = item.get('skin_of') or ''
        if parent == '' or parent == identity:
            break
        identity = parent
    return identity


#------------------------------------------------------------------------------
def same_piece(left_id, right_id, index):
    '''true when two member identities are the same vehicle or a skin of it

    german_t34_747r and german_t34_747r_camo both spawn the soviet T-34 and
    only swap the picture. that is a skin, not a different squad.
    '''
    if left_id == right_id:
        return True
    if skin_root(left_id, index) == skin_root(right_id, index):
        return True
    left = index.get(left_id) or {}
    right = index.get(right_id) or {}
    if left.get('skin_of') == right_id or right.get('skin_of') == left_id:
        return True
    parent = left.get('parent') or ''
    if parent and parent == right.get('parent'):
        shared = index.get(parent)
        if shared is not None and shared.get('kind') == 'vehicle':
            return True
    return False


#------------------------------------------------------------------------------
def member_difference(members, base_members, index):
    '''how a camo squad's members differ from its base squad

    returns (note, warning). a pure vehicle-skin swap is a note.
    any other difference is a warning.
    '''
    if members == base_members:
        return ('same members as the base squad', '')

    def counts(values):
        tally = {}
        for identity in values:
            tally[identity] = tally.get(identity, 0) + 1
        return tally

    left = counts(members)
    right = counts(base_members)
    if left == right:
        return ('same members as the base squad', '')
    identities = set(list(left.keys()) + list(right.keys()))
    swaps = []
    # pair identities that are the same vehicle with a different skin
    consumed = []
    for identity in sorted(identities):
        gap = left.get(identity, 0) - right.get(identity, 0)
        if gap == 0 or identity in consumed:
            continue
        partner = None
        for other in identities:
            if other == identity or other in consumed:
                continue
            other_gap = left.get(other, 0) - right.get(other, 0)
            if other_gap == -gap and same_piece(identity, other, index):
                partner = other
                break
        if partner is None:
            bits = []
            for changed in sorted(identities):
                changed_gap = left.get(changed, 0) - right.get(changed, 0)
                if changed_gap > 0:
                    bits.append('+' + changed)
                elif changed_gap < 0:
                    bits.append('-' + changed)
            return ('', 'members differ from the base squad: ' + ', '.join(bits))
        consumed.append(identity)
        consumed.append(partner)
        if gap > 0:
            swaps.append(partner + ' -> ' + identity)
        else:
            swaps.append(identity + ' -> ' + partner)
    if swaps:
        return ('vehicle skin: ' + ', '.join(swaps), '')
    return ('', 'members differ from the base squad')


#------------------------------------------------------------------------------
def chance_value(row, column):
    value = row.get(column)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


#------------------------------------------------------------------------------
def load_squads(path):
    '''read squad_data and resolve members, camo skins, and scenario use'''
    if os.path.exists(path) is False:
        print('database not found: ' + path)
        sys.exit(1)

    index = load_object_index(object_defs_directory())
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA query_only = ON')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [record[0] for record in cursor.fetchall()]
    if 'squad_data' not in tables:
        print('squad_data table not found in ' + path)
        connection.close()
        sys.exit(1)

    cursor.execute('SELECT * FROM squad_data')
    columns = [description[0] for description in cursor.description]
    for column in REQUIRED_COLUMNS:
        if column not in columns:
            print('squad_data is missing column ' + column)
            connection.close()
            sys.exit(1)

    raw_rows = []
    for record in cursor.fetchall():
        item = {}
        for column in columns:
            item[column] = record[column]
        raw_rows.append(item)

    scenario_rows = []
    if 'scenario_data' in tables:
        cursor.execute('SELECT * FROM scenario_data ORDER BY sort_order, id')
        scenario_columns = [description[0] for description in cursor.description]
        for record in cursor.fetchall():
            scenario = {}
            for column in scenario_columns:
                scenario[column] = record[column]
            scenario_rows.append(scenario)
    connection.close()

    by_name = {}
    seen = {}
    for item in raw_rows:
        name = item['name'] or ''
        if name in seen:
            print('warning: duplicate squad name ' + name)
        seen[name] = True
        by_name[name] = item

    scenario_use = {}
    for scenario in scenario_rows:
        label = scenario.get('name') or ''
        year = scenario.get('year')
        for side, column in (('german', 'german_squads'), ('soviet', 'soviet_squads')):
            for squad_name, count in parse_count_list(scenario.get(column)):
                if squad_name not in by_name:
                    print(
                        'warning: scenario ' + label
                        + ' lists unknown squad ' + squad_name
                    )
                    continue
                use = scenario_use.get(squad_name)
                if use is None:
                    use = []
                    scenario_use[squad_name] = use
                use.append({
                    'scenario': label,
                    'year': year,
                    'side': side,
                    'count': count,
                })

    rows = []
    for item in raw_rows:
        name = item['name'] or ''
        members = split_members(item.get('members'))
        groups = member_groups(members, index)
        soldiers = 0
        vehicles = 0
        missing = 0
        for group in groups:
            kind = group['info']['kind']
            if kind == 'soldier':
                soldiers += group['count']
            elif kind == 'vehicle':
                vehicles += group['count']
            elif kind == 'missing':
                missing += group['count']
                print('warning: ' + name + ' member has no object definition: ' + group['identity'])
        flags = []
        notes = []
        if members == []:
            flags.append('no members')
            print('warning: ' + name + ' has no members')
        for column in ('chance_1944', 'chance_1945'):
            value = item.get(column)
            if value is None or isinstance(value, int) is False or value < 0 or value > 100:
                flags.append(column + ' is ' + str(value))
                print('warning: ' + name + ' ' + column + ' is ' + str(value))
        base = camo_base_name(name)
        skins = []
        for other_name in by_name:
            if camo_base_name(other_name) == name:
                skins.append(other_name)
        skins.sort()
        if base:
            if base not in by_name:
                flags.append('camo base is not in squad_data: ' + base)
                print('warning: ' + name + ' camo base is missing: ' + base)
            else:
                notes.append(
                    'camo skin of ' + base
                    + '. quick battle rolls the base squad, then picks a skin'
                )
                base_row = by_name[base]
                if chance_value(item, 'chance_1944') != chance_value(base_row, 'chance_1944') \
                        or chance_value(item, 'chance_1945') != chance_value(base_row, 'chance_1945'):
                    flags.append('chance does not match the base squad, and this row is not rolled on its own')
                note, warning = member_difference(
                    members, split_members(base_row.get('members')), index,
                )
                if note:
                    notes.append(note)
                if warning:
                    flags.append(warning)
                    print('warning: ' + name + ' ' + warning)
        if skins:
            notes.append('skins: ' + ', '.join(skins))

        faction = item.get('faction') or ''
        for identity in members:
            prefix = None
            for candidate in ('german', 'soviet', 'civilian', 'american'):
                if identity.startswith(candidate + '_'):
                    prefix = candidate
                    break
            if prefix and faction and prefix != faction:
                message = 'member ' + identity + ' does not match faction ' + faction
                if message not in flags:
                    flags.append(message)
                    print('warning: ' + name + ' ' + message)

        try:
            cost = int(item.get('cost') or 0)
        except (TypeError, ValueError):
            cost = 0
            flags.append('cost is not a number')

        row = {
            'key': name,
            'name': name,
            'faction': faction,
            'type': item.get('type') or '',
            'category': category_for_type(item.get('type') or ''),
            'cost': cost,
            'members': members,
            'members_text': ', '.join(members),
            'groups': groups,
            'soldiers': soldiers,
            'vehicles': vehicles,
            'missing': missing,
            'size': soldiers + vehicles + missing,
            'chance_1944': chance_value(item, 'chance_1944'),
            'chance_1945': chance_value(item, 'chance_1945'),
            'camo_base': base or '',
            'skins': skins,
            'scenarios': scenario_use.get(name, []),
            'flags': flags,
            'notes': notes,
        }
        rows.append(row)
    return rows


#------------------------------------------------------------------------------
def chance_color(value):
    '''fixed color scale so a 100 chance looks the same in every view'''
    if value is None or value <= 0:
        return (232, 230, 224)
    stops = (
        (0, (232, 230, 224)),
        (20, (214, 224, 234)),
        (50, (150, 178, 204)),
        (80, (78, 116, 156)),
        (100, (36, 72, 112)),
    )
    if value >= stops[-1][0]:
        return stops[-1][1]
    for index in range(1, len(stops)):
        start_value, start_color = stops[index - 1]
        end_value, end_color = stops[index]
        if value <= end_value:
            span = end_value - start_value
            blend = (value - start_value) / span
            channels = []
            for channel in range(3):
                start = start_color[channel]
                end = end_color[channel]
                channels.append(int(start + (end - start) * blend))
            return tuple(channels)
    return stops[-1][1]


#------------------------------------------------------------------------------
def readable_ink(color):
    '''dark text on pale cells, light text on a deep fill'''
    luminance = (color[0] * 0.30) + (color[1] * 0.59) + (color[2] * 0.11)
    if luminance < 150:
        return (255, 248, 242)
    return INK


#------------------------------------------------------------------------------
def text_width(font, text):
    if text == '':
        return 0
    return font.get_rect(text).width


#------------------------------------------------------------------------------
def fit_text(font, text, max_width):
    '''truncate with an ellipsis so a label stays inside its cell'''
    if text is None:
        text = ''
    if text_width(font, text) <= max_width:
        return text
    trimmed = text
    while trimmed and text_width(font, trimmed + '...') > max_width:
        trimmed = trimmed[:-1]
    return trimmed + '...'


#------------------------------------------------------------------------------
def wrap_text(font, text, max_width):
    '''word wrap. long single words are truncated'''
    lines = []
    current = ''
    for word in text.split(' '):
        trial = word if current == '' else current + ' ' + word
        if text_width(font, trial) <= max_width:
            current = trial
            continue
        if current != '':
            lines.append(current)
        if text_width(font, word) <= max_width:
            current = word
        else:
            lines.append(fit_text(font, word, max_width))
            current = ''
    if current != '':
        lines.append(current)
    return lines


#------------------------------------------------------------------------------
class SquadReview():
    '''pygame browser for squad_data'''

    def __init__(self, rows, visible):
        pygame.init()
        pygame.freetype.init()
        self.rows = rows
        self.by_name = {}
        for row in rows:
            self.by_name[row['key']] = row

        self.filter_text = ''
        self.filter_faction = 'all'
        self.filter_category = 'all'
        self.filter_year = 'any'
        self.mode = 'roster'
        self.compared = []
        self.focus_name = None
        self.sort_column = 'name'
        self.sort_reverse = False
        self.scroll = 0
        self.status = ''
        self.hot = []
        self.quit = False

        if visible:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
            pygame.display.set_caption('TWE squad data')
            pygame.key.set_repeat(400, 50)
            self.clock = pygame.time.Clock()
        else:
            self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
            self.clock = None

        # None picks a real system font. get_default_font() warns on this machine
        self.font = pygame.freetype.SysFont(None, 14)
        self.font_small = pygame.freetype.SysFont(None, 12)
        self.font_title = pygame.freetype.SysFont(None, 20)
        self.font_value = pygame.freetype.SysFont(None, 16)

    #--------------------------------------------------------------------------
    def sort_value(self, row):
        key = self.sort_column
        if key in ('name', 'faction', 'type', 'members_text', 'category'):
            return str(row.get(key, '')).lower()
        if key in ('cost', 'size', 'soldiers', 'vehicles', 'chance_1944', 'chance_1945'):
            return row.get(key, 0)
        return row['name'].lower()

    #--------------------------------------------------------------------------
    def ordered_rows(self):
        rows = list(self.rows)
        rows.sort(
            key=lambda row: (self.sort_value(row), row['name'].lower()),
            reverse=self.sort_reverse,
        )
        return rows

    #--------------------------------------------------------------------------
    def matches(self, row, query):
        parts = [
            row['name'],
            row['faction'],
            row['type'],
            row['category'],
            row['members_text'],
            str(row['cost']),
        ]
        for group in row['groups']:
            info = group['info']
            parts.append(group['identity'])
            parts.append(info['display'])
            parts.append(info['gear'])
            parts.append(info['kind'])
        for use in row['scenarios']:
            parts.append(use['scenario'])
        for note in row['notes']:
            parts.append(note)
        haystack = ' '.join(parts).lower()
        return query in haystack

    #--------------------------------------------------------------------------
    def filtered_rows(self):
        query = self.filter_text.strip().lower()
        result = []
        for row in self.ordered_rows():
            if self.filter_faction != 'all' and row['faction'] != self.filter_faction:
                continue
            if self.filter_category != 'all' and row['category'] != self.filter_category:
                continue
            if self.filter_year == '1944' and row['chance_1944'] <= 0:
                continue
            if self.filter_year == '1945' and row['chance_1945'] <= 0:
                continue
            if query and self.matches(row, query) is False:
                continue
            result.append(row)
        return result

    #--------------------------------------------------------------------------
    def rows_on_screen(self):
        if self.mode == 'table':
            return max(1, (BODY_H - TABLE_HEADER_H) // TABLE_ROW_H)
        return max(1, (BODY_H - LIST_HEADER_H) // LIST_ROW_H)

    #--------------------------------------------------------------------------
    def clamp_scroll(self):
        window = self.rows_on_screen()
        limit = max(0, len(self.filtered_rows()) - window)
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > limit:
            self.scroll = limit

    #--------------------------------------------------------------------------
    def reveal_focus(self):
        names = [row['key'] for row in self.filtered_rows()]
        if self.focus_name not in names:
            return
        index = names.index(self.focus_name)
        window = self.rows_on_screen()
        if index < self.scroll:
            self.scroll = index
        elif index >= self.scroll + window:
            self.scroll = index - window + 1

    #--------------------------------------------------------------------------
    def move_focus(self, delta):
        rows = self.filtered_rows()
        if not rows:
            return
        names = [row['key'] for row in rows]
        if self.focus_name in names:
            index = names.index(self.focus_name) + delta
            index = max(0, min(len(names) - 1, index))
        elif delta < 0:
            index = len(names) - 1
        else:
            index = 0
        self.focus_name = names[index]
        self.reveal_focus()

    #--------------------------------------------------------------------------
    def show_only(self, name):
        self.compared = [name]
        self.focus_name = name
        self.status = ''

    #--------------------------------------------------------------------------
    def show_toggle(self, name):
        self.focus_name = name
        if name in self.compared:
            self.compared.remove(name)
            self.status = ''
            return
        if len(self.compared) >= MAX_COMPARE:
            self.status = 'limit is ' + str(MAX_COMPARE) + ' squads. remove one first'
            return
        self.compared.append(name)
        self.status = ''

    #--------------------------------------------------------------------------
    def compare_visible(self):
        rows = self.filtered_rows()
        if not rows:
            self.status = 'nothing matches the filter'
            return
        self.compared = [row['key'] for row in rows[:MAX_COMPARE]]
        self.focus_name = self.compared[0]
        if len(rows) > MAX_COMPARE:
            self.status = (
                'comparing ' + str(MAX_COMPARE) + ' of ' + str(len(rows))
                + ' matching squads. narrow the filter to see the rest'
            )
        else:
            self.status = ''

    #--------------------------------------------------------------------------
    def color_for(self, name):
        if name not in self.compared:
            return None
        return PLOT_COLORS[self.compared.index(name) % len(PLOT_COLORS)]

    #--------------------------------------------------------------------------
    def set_sort(self, key):
        if self.sort_column == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = key
            # text reads A to Z first. numbers read high to low first
            self.sort_reverse = key not in ('name', 'faction', 'type', 'members_text', 'category')
        self.scroll = 0

    #--------------------------------------------------------------------------
    def mark_header(self, rect, key):
        '''tint the sorted column'''
        if self.sort_column != key:
            return
        pygame.draw.rect(self.screen, (214, 226, 236), rect)
        pygame.draw.line(
            self.screen, ACCENT,
            (rect.left, rect.bottom - 1), (rect.right, rect.bottom - 1), 2,
        )

    #--------------------------------------------------------------------------
    def hit(self, pos):
        for rect, action, payload in reversed(self.hot):
            if rect.collidepoint(pos):
                return action, payload
        return None, None

    #--------------------------------------------------------------------------
    def handle_click(self, pos, toggle):
        action, payload = self.hit(pos)
        if action is None:
            return
        if action == 'faction':
            self.filter_faction = payload
            self.scroll = 0
        elif action == 'category':
            self.filter_category = payload
            self.scroll = 0
        elif action == 'year':
            self.filter_year = payload
            self.scroll = 0
        elif action == 'mode':
            self.mode = payload
            self.reveal_focus()
        elif action == 'compare_visible':
            self.compare_visible()
        elif action == 'sort':
            self.set_sort(payload)
        elif action == 'row':
            if toggle:
                self.show_toggle(payload)
            else:
                self.show_only(payload)
        elif action == 'focus':
            self.focus_name = payload

    #--------------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
            return
        if event.type == pygame.TEXTINPUT:
            mods = pygame.key.get_mods()
            if mods & (pygame.KMOD_CTRL | pygame.KMOD_META):
                return
            self.filter_text += event.text
            self.scroll = 0
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll -= event.y
            self.clamp_scroll()
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mods = pygame.key.get_mods()
                toggle = bool(mods & (pygame.KMOD_SHIFT | pygame.KMOD_CTRL | pygame.KMOD_META))
                self.handle_click(event.pos, toggle)
            elif event.button == 3:
                self.handle_click(event.pos, True)
            return
        if event.type != pygame.KEYDOWN:
            return

        mods = event.mod
        if event.key == pygame.K_q and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
            self.quit = True
        elif event.key == pygame.K_p and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
            self.compare_visible()
        elif event.key == pygame.K_ESCAPE:
            if self.filter_text:
                self.filter_text = ''
                self.scroll = 0
            else:
                self.compared = []
                self.status = ''
        elif event.key == pygame.K_BACKSPACE:
            self.filter_text = self.filter_text[:-1]
            self.scroll = 0
        elif event.key == pygame.K_DOWN:
            self.move_focus(1)
        elif event.key == pygame.K_UP:
            self.move_focus(-1)
        elif event.key == pygame.K_PAGEUP:
            self.move_focus(-self.rows_on_screen())
        elif event.key == pygame.K_PAGEDOWN:
            self.move_focus(self.rows_on_screen())
        elif event.key == pygame.K_HOME:
            self.scroll = 0
            rows = self.filtered_rows()
            if rows:
                self.focus_name = rows[0]['key']
        elif event.key == pygame.K_END:
            rows = self.filtered_rows()
            if rows:
                self.focus_name = rows[-1]['key']
                self.reveal_focus()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.focus_name is None:
                return
            if mods & pygame.KMOD_SHIFT:
                self.show_toggle(self.focus_name)
            else:
                self.show_only(self.focus_name)

    #--------------------------------------------------------------------------
    def blit(self, font, text, pos, color):
        if text is None or text == '':
            return 0
        rendered, _rect = font.render(text, fgcolor=color)
        self.screen.blit(rendered, pos)
        return rendered.get_width()

    #--------------------------------------------------------------------------
    def blit_in(self, font, text, rect, color, align):
        if text is None:
            text = ''
        rendered, _rect = font.render(text, fgcolor=color)
        if align == 'center':
            x = rect.x + (rect.width - rendered.get_width()) // 2
        elif align == 'right':
            x = rect.right - rendered.get_width() - 6
        else:
            x = rect.x + 6
        y = rect.y + (rect.height - rendered.get_height()) // 2
        self.screen.blit(rendered, (x, y))

    #--------------------------------------------------------------------------
    def chip(self, label, x, y, active, action, payload):
        width = text_width(self.font, label) + 18
        rect = pygame.Rect(x, y, width, 26)
        if active:
            fill = ACCENT
            color = WHITE
            border = ACCENT
        else:
            fill = WHITE
            color = INK
            border = LINE
        pygame.draw.rect(self.screen, fill, rect, border_radius=5)
        pygame.draw.rect(self.screen, border, rect, 1, border_radius=5)
        self.blit_in(self.font, label, rect, color, 'center')
        self.hot.append((rect, action, payload))
        return width

    #--------------------------------------------------------------------------
    def draw_bar(self, rect, fraction, color):
        pygame.draw.rect(self.screen, (232, 230, 224), rect, border_radius=3)
        fraction = max(0.0, min(1.0, fraction))
        if fraction > 0:
            fill_w = max(2, int(rect.width * fraction))
            fill = pygame.Rect(rect.x, rect.y, fill_w, rect.height)
            pygame.draw.rect(self.screen, color, fill, border_radius=3)
        pygame.draw.rect(self.screen, LINE, rect, 1, border_radius=3)

    #--------------------------------------------------------------------------
    def render_top(self):
        self.blit(self.font_title, 'squad data', (MARGIN, 12), INK)
        shown = len(self.filtered_rows())
        broken = 0
        for row in self.rows:
            broken += row['missing']
        count = str(shown) + ' of ' + str(len(self.rows)) + ' shown'
        if self.compared:
            count += '    ' + str(len(self.compared)) + ' compared'
        if broken:
            count += '    ' + str(broken) + ' broken member references'
        count_color = WARN if broken else MUTED
        self.blit(self.font_small, count, (MARGIN, 42), count_color)

        search = pygame.Rect(210, 14, 250, 26)
        pygame.draw.rect(self.screen, WHITE, search, border_radius=5)
        pygame.draw.rect(self.screen, LINE, search, 1, border_radius=5)
        if self.filter_text:
            shown_text = fit_text(self.font, self.filter_text, search.width - 16)
            color = INK
        else:
            shown_text = 'name, type, weapon, member'
            color = MUTED
        self.blit(self.font, shown_text, (search.x + 8, search.y + 5), color)
        if self.filter_text:
            caret_x = search.x + 8 + text_width(self.font, shown_text) + 1
            pygame.draw.line(
                self.screen, ACCENT,
                (caret_x, search.y + 5), (caret_x, search.bottom - 5), 1,
            )

        x = search.right + 12
        for value, label in (('all', 'all'), ('german', 'german'), ('soviet', 'soviet'), ('civilian', 'civilian')):
            x += self.chip(label, x, 14, self.filter_faction == value, 'faction', value) + 6

        mode_labels = (('roster', 'roster'), ('table', 'table'))
        mode_widths = [text_width(self.font, label) + 18 for _value, label in mode_labels]
        mode_x = SCREEN_W - MARGIN - sum(mode_widths) - 6 * (len(mode_labels) - 1)
        for index, (value, label) in enumerate(mode_labels):
            self.chip(label, mode_x, 14, self.mode == value, 'mode', value)
            mode_x += mode_widths[index] + 6

        x = 210
        for value, label in (('any', 'any year'), ('1944', '1944'), ('1945', '1945')):
            x += self.chip(label, x, 50, self.filter_year == value, 'year', value) + 6
        for value in CATEGORY_ORDER:
            x += self.chip(value, x, 50, self.filter_category == value, 'category', value) + 6

    #--------------------------------------------------------------------------
    def faction_mark(self, row, x, y, height):
        color = FACTION_COLOR.get(row['faction'], MUTED)
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y + 4, 6, height - 8))

    #--------------------------------------------------------------------------
    def list_header_rects(self, panel):
        y = panel.y
        height = LIST_HEADER_H
        specs = (
            ('name', 'name', 8, 322),
            ('type', 'type', 330, 158),
            ('cost', 'cost', 488, 48),
            ('chance_1944', '1944', 536, 48),
            ('chance_1945', '1945', 584, 52),
        )
        headers = []
        for key, label, x, width in specs:
            rect = pygame.Rect(panel.x + x, y, width, height)
            headers.append((key, label, rect))
        return headers

    #--------------------------------------------------------------------------
    def render_list(self):
        panel = pygame.Rect(MARGIN, BODY_Y, LIST_W, BODY_H)
        pygame.draw.rect(self.screen, PANEL, panel)
        pygame.draw.rect(self.screen, LINE, panel, 1)

        for key, label, rect in self.list_header_rects(panel):
            self.mark_header(rect, key)
            align = 'left'
            if key in ('cost', 'chance_1944', 'chance_1945'):
                align = 'right'
            self.blit_in(self.font_small, label, rect, MUTED, align)
            self.hot.append((rect, 'sort', key))
        pygame.draw.line(
            self.screen, LINE,
            (panel.x, panel.y + LIST_HEADER_H),
            (panel.right, panel.y + LIST_HEADER_H),
            1,
        )

        rows = self.filtered_rows()
        body = pygame.Rect(panel.x, panel.y + LIST_HEADER_H, panel.width, panel.height - LIST_HEADER_H)
        self.screen.set_clip(body)
        y = body.y
        for row in rows[self.scroll:]:
            if y + LIST_ROW_H > body.bottom:
                break
            row_rect = pygame.Rect(panel.x + 1, y, panel.width - 2, LIST_ROW_H)
            if row['key'] == self.focus_name:
                pygame.draw.rect(self.screen, FOCUS, row_rect)
            color = self.color_for(row['key'])
            self.faction_mark(row, panel.x + 4, y, LIST_ROW_H)
            if color is not None:
                pygame.draw.rect(
                    self.screen, color,
                    pygame.Rect(panel.x + 12, y + 4, 6, LIST_ROW_H - 8),
                )
            name_color = INK
            if row['flags']:
                name_color = WARN
            elif color is not None:
                name_color = color
            name = fit_text(self.font, row['name'], 304)
            self.blit(self.font, name, (panel.x + 22, y + 4), name_color)
            self.blit_in(
                self.font_small,
                fit_text(self.font_small, row['type'], 146),
                pygame.Rect(panel.x + 330, y, 158, LIST_ROW_H),
                MUTED, 'left',
            )
            self.blit_in(
                self.font, str(row['cost']),
                pygame.Rect(panel.x + 488, y, 42, LIST_ROW_H),
                INK, 'right',
            )
            self.blit_in(
                self.font_small, str(row['chance_1944']),
                pygame.Rect(panel.x + 536, y, 42, LIST_ROW_H),
                INK, 'right',
            )
            self.blit_in(
                self.font_small, str(row['chance_1945']),
                pygame.Rect(panel.x + 584, y, 46, LIST_ROW_H),
                INK, 'right',
            )
            self.hot.append((row_rect, 'row', row['key']))
            y += LIST_ROW_H
        self.screen.set_clip(None)

        if not rows:
            self.blit(self.font, 'no squads match', (panel.x + 14, body.y + 12), MUTED)

    #--------------------------------------------------------------------------
    def table_columns(self, panel):
        columns = [
            ('name', 'name', 280),
            ('faction', 'faction', 78),
            ('type', 'type', 150),
            ('cost', 'cost', 54),
            ('soldiers', 'men', 46),
            ('vehicles', 'veh', 46),
            ('chance_1944', '1944', 52),
            ('chance_1945', '1945', 52),
        ]
        used = 0
        for _key, _label, width in columns:
            used += width
        columns.append(('members_text', 'members', panel.width - used))
        laid = []
        x = panel.x
        for key, label, width in columns:
            laid.append((key, label, pygame.Rect(x, panel.y, width, TABLE_HEADER_H)))
            x += width
        return laid

    #--------------------------------------------------------------------------
    def render_table(self):
        panel = pygame.Rect(MARGIN, BODY_Y, SCREEN_W - MARGIN * 2, BODY_H)
        pygame.draw.rect(self.screen, PANEL, panel)
        pygame.draw.rect(self.screen, LINE, panel, 1)
        columns = self.table_columns(panel)

        for key, label, rect in columns:
            self.hot.append((rect, 'sort', key))
            self.mark_header(rect, key)
            if key in ('name', 'faction', 'type', 'members_text'):
                align = 'left'
            else:
                align = 'center'
            self.blit_in(self.font_small, label, rect, MUTED, align)
        pygame.draw.line(
            self.screen, LINE,
            (panel.x, panel.y + TABLE_HEADER_H),
            (panel.right, panel.y + TABLE_HEADER_H),
            1,
        )

        rows = self.filtered_rows()
        body = pygame.Rect(panel.x, panel.y + TABLE_HEADER_H, panel.width, panel.height - TABLE_HEADER_H)
        self.screen.set_clip(body)
        y = body.y
        for row in rows[self.scroll:]:
            if y + TABLE_ROW_H > body.bottom:
                break
            row_rect = pygame.Rect(panel.x + 1, y, panel.width - 2, TABLE_ROW_H)
            if row['key'] == self.focus_name:
                pygame.draw.rect(self.screen, FOCUS, row_rect)
            color = self.color_for(row['key'])
            if color is not None:
                pygame.draw.rect(self.screen, color, pygame.Rect(panel.x + 1, y + 3, 8, TABLE_ROW_H - 6))
            for key, _label, header in columns:
                cell = pygame.Rect(header.x, y, header.width, TABLE_ROW_H)
                if key == 'name':
                    self.faction_mark(row, cell.x + 4, y, TABLE_ROW_H)
                    label = fit_text(self.font_small, row['name'], cell.width - 24)
                    ink = WARN if row['flags'] else INK
                    if color is not None and row['flags'] == []:
                        ink = color
                    name_cell = pygame.Rect(cell.x + 8, cell.y, cell.width - 8, cell.height)
                    self.blit_in(self.font_small, label, name_cell, ink, 'left')
                elif key == 'faction':
                    self.blit_in(self.font_small, row['faction'], cell, MUTED, 'left')
                elif key == 'type':
                    label = fit_text(self.font_small, row['type'], cell.width - 12)
                    self.blit_in(self.font_small, label, cell, INK, 'left')
                elif key == 'members_text':
                    label = fit_text(self.font_small, row['members_text'], cell.width - 12)
                    ink = WARN if row['missing'] else MUTED
                    self.blit_in(self.font_small, label, cell, ink, 'left')
                elif key in ('chance_1944', 'chance_1945'):
                    value = row[key]
                    fill = chance_color(value)
                    inset = pygame.Rect(cell.x + 2, cell.y + 2, cell.width - 4, cell.height - 4)
                    pygame.draw.rect(self.screen, fill, inset)
                    self.blit_in(self.font_small, str(value), cell, readable_ink(fill), 'center')
                else:
                    self.blit_in(self.font_small, str(row[key]), cell, INK, 'center')
            self.hot.append((row_rect, 'row', row['key']))
            y += TABLE_ROW_H
        self.screen.set_clip(None)
        if not rows:
            self.blit(self.font, 'no squads match', (panel.x + 14, body.y + 12), MUTED)

    #--------------------------------------------------------------------------
    def render_chance_block(self, rect, row, swatch):
        '''one squad's 1944 and 1945 chances as two bars'''
        label_w = 36
        value_w = 28
        gap = 8
        bar_w = (rect.width - label_w * 2 - value_w * 2 - gap) // 2
        if bar_w < 20:
            bar_w = 20
        y = rect.y + (rect.height - 14) // 2
        x = rect.x
        if swatch is not None:
            pygame.draw.rect(self.screen, swatch, pygame.Rect(rect.x, rect.y + 4, 8, rect.height - 8))
            x = rect.x + 14
        self.blit(self.font_small, '1944', (x, y), MUTED)
        bar = pygame.Rect(x + label_w, y, bar_w, 14)
        self.draw_bar(bar, row['chance_1944'] / 100.0, BAR_1944)
        self.blit(self.font_small, str(row['chance_1944']), (bar.right + 4, y), INK)
        x2 = bar.right + value_w + gap
        self.blit(self.font_small, '1945', (x2, y), MUTED)
        bar2 = pygame.Rect(x2 + label_w, y, bar_w, 14)
        self.draw_bar(bar2, row['chance_1945'] / 100.0, BAR_1945)
        self.blit(self.font_small, str(row['chance_1945']), (bar2.right + 4, y), INK)

    #--------------------------------------------------------------------------
    def render_chances(self, panel):
        self.blit(self.font, 'year chance', (panel.x + 12, panel.y + 8), INK)
        self.blit(
            self.font_small,
            '0 to 100. quick battle rolls this before it will buy the squad.',
            (panel.x + 110, panel.y + 10),
            MUTED,
        )
        if not self.compared:
            hint = 'Click a squad to see its chances and roster. Shift-click to compare.'
            self.blit(self.font, hint, (panel.x + 12, panel.y + 46), MUTED)
            return

        if len(self.compared) == 1:
            row = self.by_name.get(self.compared[0])
            if row is None:
                return
            color = self.color_for(row['key'])
            self.blit(self.font_value, row['name'], (panel.x + 12, panel.y + 36), color)
            block = pygame.Rect(panel.x + 12, panel.y + 68, panel.width - 24, 28)
            self.render_chance_block(block, row, None)
            return

        y = panel.y + 32
        for name in self.compared:
            row = self.by_name.get(name)
            if row is None:
                continue
            if y + 48 > panel.bottom:
                break
            color = self.color_for(name)
            line = pygame.Rect(panel.x + 8, y, panel.width - 16, 46)
            if name == self.focus_name:
                pygame.draw.rect(self.screen, FOCUS, line, border_radius=3)
            pygame.draw.rect(self.screen, color, pygame.Rect(panel.x + 14, y + 6, 8, 10))
            label = fit_text(self.font, row['name'], panel.width - 40)
            self.blit(self.font, label, (panel.x + 28, y + 3), color)
            block = pygame.Rect(panel.x + 12, y + 22, panel.width - 24, 18)
            self.render_chance_block(block, row, None)
            self.hot.append((line, 'focus', name))
            y += 48

    #--------------------------------------------------------------------------
    def render_roster(self, panel):
        pygame.draw.line(
            self.screen, LINE,
            (panel.x, panel.y), (panel.right, panel.y), 1,
        )
        row = None
        if self.focus_name is not None:
            row = self.by_name.get(self.focus_name)
        title = 'roster'
        if row is not None:
            bits = []
            if row['soldiers']:
                bits.append(str(row['soldiers']) + ' soldiers')
            if row['vehicles']:
                bits.append(str(row['vehicles']) + ' vehicles')
            if row['missing']:
                bits.append(str(row['missing']) + ' missing')
            if bits:
                title += '    ' + ', '.join(bits)
        title_color = WARN if row is not None and row['missing'] else INK
        self.blit(self.font, title, (panel.x + 12, panel.y + 8), title_color)
        if row is None:
            self.blit(self.font, 'Select a squad.', (panel.x + 12, panel.y + 36), MUTED)
            return

        header_y = panel.y + 32
        self.blit(self.font_small, 'n', (panel.x + 12, header_y), MUTED)
        self.blit(self.font_small, 'resolved', (panel.x + 44, header_y), MUTED)
        self.blit(self.font_small, 'identity', (panel.x + 280, header_y), MUTED)
        self.blit(self.font_small, 'kind', (panel.x + 530, header_y), MUTED)
        self.blit(self.font_small, 'carried', (panel.x + 610, header_y), MUTED)

        y = header_y + 18
        for group in row['groups']:
            if y + 22 > panel.bottom:
                self.blit(self.font_small, 'more members below the fold', (panel.x + 12, y), MUTED)
                break
            info = group['info']
            if info['kind'] == 'missing':
                ink = WARN
            elif info['kind'] == 'vehicle':
                ink = VEHICLE_COLOR
            elif info['kind'] == 'soldier':
                ink = SOLDIER_COLOR
            else:
                ink = INK
            self.blit(self.font, str(group['count']), (panel.x + 12, y + 2), INK)
            display = fit_text(self.font, info['display'], 220)
            self.blit(self.font, display, (panel.x + 44, y + 2), ink)
            identity = fit_text(self.font_small, group['identity'], 240)
            self.blit(self.font_small, identity, (panel.x + 280, y + 4), MUTED)
            self.blit(self.font_small, info['kind'], (panel.x + 530, y + 4), ink)
            if info['gear']:
                gear = fit_text(self.font_small, info['gear'], panel.right - (panel.x + 610) - 12)
                self.blit(self.font_small, gear, (panel.x + 610, y + 4), INK)
            y += 22

    #--------------------------------------------------------------------------
    def render_side(self):
        panel = pygame.Rect(
            MARGIN + LIST_W + 10, BODY_Y,
            SCREEN_W - LIST_W - MARGIN * 2 - 10, BODY_H,
        )
        pygame.draw.rect(self.screen, PANEL, panel)
        pygame.draw.rect(self.screen, LINE, panel, 1)
        if len(self.compared) > 1:
            chart_h = 36 + 48 * len(self.compared)
        else:
            chart_h = 112
        chart_h = min(chart_h, panel.height // 2)
        self.render_chances(pygame.Rect(panel.x, panel.y, panel.width, chart_h))
        self.render_roster(pygame.Rect(panel.x, panel.y + chart_h, panel.width, panel.height - chart_h))

    #--------------------------------------------------------------------------
    def render_detail(self):
        rect = pygame.Rect(MARGIN, DETAIL_Y, SCREEN_W - MARGIN * 2, DETAIL_H)
        pygame.draw.rect(self.screen, PANEL, rect)
        pygame.draw.rect(self.screen, LINE, rect, 1)
        row = None
        if self.focus_name is not None:
            row = self.by_name.get(self.focus_name)
        if row is None:
            self.blit(self.font, 'Select a squad.', (rect.x + 12, rect.y + 12), MUTED)
            return

        color = self.color_for(row['key'])
        name_color = color if color is not None else INK
        if row['flags']:
            name_color = WARN
        self.faction_mark(row, rect.x + 8, rect.y + 8, 22)
        self.blit(self.font_title, row['name'], (rect.x + 20, rect.y + 8), name_color)

        stats = '   '.join([
            row['faction'],
            row['type'],
            'budget ' + row['category'],
            'cost ' + str(row['cost']),
            str(row['size']) + ' members',
            str(row['chance_1944']) + ' in 1944',
            str(row['chance_1945']) + ' in 1945',
        ])
        self.blit(
            self.font_small,
            fit_text(self.font_small, stats, rect.width - 36),
            (rect.x + 20, rect.y + 34),
            INK,
        )

        mix = pygame.Rect(rect.x + 20, rect.y + 52, 280, 12)
        total = row['size']
        if total > 0:
            pygame.draw.rect(self.screen, (232, 230, 224), mix, border_radius=3)
            cursor = mix.x
            segments = (
                (row['soldiers'], SOLDIER_COLOR),
                (row['vehicles'], VEHICLE_COLOR),
                (row['missing'], WARN),
            )
            for count, fill in segments:
                if count <= 0:
                    continue
                width = int(mix.width * (count / float(total)))
                if width < 2:
                    width = 2
                pygame.draw.rect(
                    self.screen, fill,
                    pygame.Rect(cursor, mix.y, width, mix.height),
                )
                cursor += width
            pygame.draw.rect(self.screen, LINE, mix, 1, border_radius=3)
        mix_label = str(row['soldiers']) + ' soldiers    ' + str(row['vehicles']) + ' vehicles'
        if row['missing']:
            mix_label += '    ' + str(row['missing']) + ' missing'
        self.blit(self.font_small, mix_label, (mix.right + 10, mix.y - 1), MUTED)

        y = rect.y + 76
        note_text = '  '.join(row['notes'])
        if note_text:
            for line in wrap_text(self.font_small, note_text, rect.width - 36)[:2]:
                self.blit(self.font_small, line, (rect.x + 20, y), MUTED)
                y += 14
        if row['scenarios']:
            bits = []
            for use in row['scenarios']:
                year = ''
                if use['year']:
                    year = ' ' + str(use['year'])
                bits.append(use['scenario'] + year + ' x' + str(use['count']))
            scenario_text = 'scenarios: ' + ', '.join(bits)
        else:
            scenario_text = 'scenarios: none. it can still be rolled into a quick battle'
        for line in wrap_text(self.font_small, scenario_text, rect.width - 36)[:2]:
            self.blit(self.font_small, line, (rect.x + 20, y), INK)
            y += 14
        if row['flags']:
            self.blit(
                self.font_small,
                fit_text(self.font_small, '   '.join(row['flags']), rect.width - 36),
                (rect.x + 20, y),
                WARN,
            )
            y += 14
        members = 'members: ' + row['members_text']
        for line in wrap_text(self.font_small, members, rect.width - 36)[:2]:
            self.blit(self.font_small, line, (rect.x + 20, y), MUTED)
            y += 14

    #--------------------------------------------------------------------------
    def render_help(self):
        if self.status:
            self.blit(self.font_small, self.status, (MARGIN, SCREEN_H - 18), WARN)
            return
        help_text = (
            'click: show one    shift-click or right-click: compare    '
            'ctrl-p: compare shown    arrows: move    enter: show    '
            'esc: clear filter, then clear comparison    ctrl-q: quit    '
            'color mark: faction    second mark: in the comparison'
        )
        self.blit(self.font_small, help_text, (MARGIN, SCREEN_H - 18), MUTED)

    #--------------------------------------------------------------------------
    def render(self):
        self.hot = []
        self.clamp_scroll()
        self.screen.fill(BG)
        self.render_top()
        if self.mode == 'table':
            self.render_table()
        else:
            self.render_list()
            self.render_side()
        self.render_detail()
        self.render_help()
        if self.clock is not None:
            pygame.display.flip()


#------------------------------------------------------------------------------
def print_usage():
    print('Usage: python squad_data_tool.py [data.sqlite]')
    print('  python3 code/tools/squad_data_tool.py')
    print('Opens a list and table of squad_data, with members resolved to soldiers and vehicles.')
    print('  --check          draw a few views to png files and exit')
    print('  --shots <folder> open a window, save the same views, and exit')


#------------------------------------------------------------------------------
def select_squad(tool, name):
    '''focus one squad. returns False when that name is not in the table'''
    if name not in tool.by_name:
        print('warning: sample squad missing: ' + name)
        return False
    tool.show_only(name)
    tool.reveal_focus()
    return True


#------------------------------------------------------------------------------
def save_view(tool, folder, filename):
    tool.render()
    # let the window map before the pixels are copied out
    if tool.clock is not None:
        pygame.event.pump()
        tool.render()
    path = os.path.join(folder, filename)
    pygame.image.save(tool.screen, path)
    print(path)
    return path


#------------------------------------------------------------------------------
def render_sample_views(tool, folder):
    '''three views: the squad list, one squad's roster, and the full table'''
    if os.path.isdir(folder) is False:
        os.makedirs(folder)

    tool.mode = 'roster'
    tool.filter_text = ''
    tool.filter_faction = 'all'
    tool.filter_category = 'all'
    tool.filter_year = 'any'
    tool.sort_column = 'name'
    tool.sort_reverse = False
    tool.scroll = 0
    if select_squad(tool, 'German 1944 Rifle') is False and tool.rows:
        tool.show_only(tool.rows[0]['key'])
        tool.reveal_focus()
    save_view(tool, folder, 'squad_list.png')

    tool.mode = 'roster'
    tool.filter_text = ''
    tool.scroll = 0
    found = select_squad(tool, 'German Panzerjager Tiger P')
    if found and 'German Panzerjager Tiger P camo1' in tool.by_name:
        tool.show_toggle('German Panzerjager Tiger P camo1')
        tool.focus_name = 'German Panzerjager Tiger P'
        tool.reveal_focus()
    save_view(tool, folder, 'squad_detail.png')

    tool.mode = 'table'
    tool.compared = []
    tool.filter_text = ''
    tool.set_sort('cost')
    if select_squad(tool, 'Soviet T34-85') is False and tool.filtered_rows():
        tool.show_only(tool.filtered_rows()[0]['key'])
        tool.reveal_focus()
    # table view is the whole list. keep the focus, drop the compare marks
    focused = tool.focus_name
    tool.compared = []
    tool.focus_name = focused
    save_view(tool, folder, 'squad_table.png')

    soldiers = 0
    vehicles = 0
    missing = 0
    flagged = 0
    for row in tool.rows:
        soldiers += row['soldiers']
        vehicles += row['vehicles']
        missing += row['missing']
        if row['flags']:
            flagged += 1
    print('squads ' + str(len(tool.rows)))
    print('soldier members ' + str(soldiers))
    print('vehicle members ' + str(vehicles))
    print('missing members ' + str(missing))
    print('squads with warnings ' + str(flagged))


#------------------------------------------------------------------------------
def main():
    check = False
    shots = None
    path = database_path()
    args = sys.argv[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == '--check':
            check = True
        elif arg == '--shots':
            index += 1
            if index >= len(args):
                print('--shots needs a folder')
                return
            shots = args[index]
        elif arg in ('-h', '--help'):
            print_usage()
            return
        else:
            path = arg
        index += 1

    rows = load_squads(path)
    visible = shots is not None
    if check and shots is None:
        visible = False
    tool = SquadReview(rows, visible=visible or (check is False and shots is None))
    if shots is not None:
        print('display ' + pygame.display.get_driver())
        render_sample_views(tool, shots)
        return
    if check:
        folder = os.environ.get('SQUAD_TOOL_OUT', '/tmp')
        render_sample_views(tool, folder)
        return

    while tool.quit is False:
        for event in pygame.event.get():
            tool.handle_event(event)
        tool.render()
        tool.clock.tick(30)


if __name__ == '__main__':
    main()
