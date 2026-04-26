# AGENTS.md
## For AI assistants working on TWE (To Whatever End)

Python/Pygame WW2 tactical simulation. Simulates individual soldiers and vehicles with realistic physics, AI, and penetration mechanics.

---

## Quick Commands

```bash
# test run that skips menus with manual actions :
cd code && python3 twe.py --quick-battle civilian 2

# Lint (pylint)
pip install pylint
pylint code/engine/world.py

# Profile
python3 -m cProfile -o profile.prof twe.py
snakeviz profile.prof

# Tools
cd code/tools
python3 armor_thickness.py 20 60  # Calc effective armor
python3 image_tool.py  # Sprite alignment GUI
```

**Controls**: WASD move, F fire, TAB menu, ~ debug, [ ] zoom

---

## Code Structure

```
code/
  twe.py              # Entry point (screen size: 1920x1080)
  engine/             # Core game: world.py (~970 lines), graphics_2d_pygame.py
  ai/                 # 35+ AI modules: ai_human.py (~2700 lines), ai_faction_tactical.py
  data/               # holds the main database
  tools/              # armor_thickness.py, image_tool.py
```

**Key Files**:
- `engine/world.py` - Main simulation loop
- `engine/graphics_2d_pygame.py` - Rendering
- `ai/ai_human.py` - Human AI (task dispatch via `self.task_map`)
- `engine/vehicle_diagnostics.py` - Vehicle debug screens

---

## Code Style

### Imports
```python
# Builtins
import random
import copy

# Local (absolute paths)
from engine.graphics_2d_pygame import Graphics_2D_Pygame
import engine.math_2d
```
- Order: Builtins > locals. No relative imports (except intra-dir). No `typing` or `from __future__`.

### Naming
- `snake_case`: vars/functions (`world_coords`, `update_task_engage_enemy`)
- `PascalCase`: classes (`AIHuman`, `World`)
- `lower` abbreviations: `ai`, `wo` (WorldObject)

### Formatting
- 4-space indent, 40-char line for long conditionals OK
- 1 blank line between funcs/classes
- Double quotes for strings, single for dict keys

### Patterns
- **AI State**: `self.memory = {}` dict, dispatch via `self.task_map['task_name']()`
- **Queues**: `add_queue`, `remove_queue` for thread-safe world ops
- **Coords**: `world_coords` = `[x, y]` list; `screen_coords` for display
- **Long methods OK**: `update()` can be 100-500+ lines (AI dispatchers)

### Error Handling
- Minimal try/except. Prefer centralized logging:
  ```python
  engine.log.add_data('error', 'msg', True)
  ```
- No `raise`. Validate early: `if obj is None: return`

### Comments
- **NEVER add comments unless requested**
- Module header: triple-quote with repo URL
- Inline: `# note - ...` for TODOs only

---

## Key Conventions

### AI Task Dispatch
```python
self.memory['task'] = {'state': 'foo', 'target': target}
self.task_map[self.memory['task']['current_task']]()
```

### Vehicle/Magazine Access
```python
# Check ammo (in ai_human.py)
ammo_gun, ammo_inventory, magazine_count = self.check_ammo(weapon, vehicle)

# Compatible magazines: vehicle.ai.inventory + vehicle.ai.ammo_rack
# Filter by: magazine.is_gun_magazine and weapon.world_builder_identity in magazine.ai.compatible_guns
```

### World Object Properties
- `is_vehicle`, `is_human`, `is_gun_magazine`
- `ai.inventory`, `ai.ammo_rack` (vehicles)
- `ai.projectiles` (magazine contents)
- `ai.projectile_type` (projectile categorization)

---

## Post-Edit Workflow
1. Lint: `pylint <file.py>`
2. Run: `python3 twe.py` (check for crashes/visual issues)

---

## Git
- `main`: stable, `dev`: active development
- **NEVER commit/push without explicit request**
