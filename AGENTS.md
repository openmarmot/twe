# AGENTS.md
## For AI assistants working on TWE (To Whatever End)

Python/Pygame WW2 tactical simulation. Simulates individual soldiers and vehicles with realistic physics, AI, and penetration mechanics.

---

## Quick Commands

```bash
# AI testing - runs quick battle and exits after N seconds (excellent for smoke-testing vehicle/AI changes):
bash start.sh --ai-test civilian 3

# Lint (pylint) - expect import noise + pre-existing style issues; focus on *new* errors from your changes
pip install pylint
pylint code/ai/ai_vehicle.py code/ai/ai_human_vehicle_driver.py --disable=import-error

# Profile
bash run_profile.sh --ai-test civilian 3
# (opens snakeviz)

# Tools
cd code/tools
python3 armor_thickness.py 20 60  # Calc effective armor
python3 image_tool.py  # Sprite alignment GUI
```

**Controls**: WASD move, F fire, TAB menu, ~ debug (vehicle diagnostics), [ ] zoom

**Vehicle/AI debugging tip**: Use `--ai-test` + the ~ debug overlay + vehicle_diagnostics.py for rotation/throttle/brake issues. Heavy vehicles + casemates frequently exercise the ROTATING path.

---

## Code Structure

```
code/
  twe.py              # Entry point (run via start.sh; screen_size="auto")
  engine/             # Core game + world_builder.py (vehicle defs)
  ai/                 # 35+ AI modules: ai_human.py (~2700 lines), ai_vehicle.py (physics), ai_human_vehicle_*.py (crew)
  data/               # holds the main database
  tools/              # armor_thickness.py, image_tool.py
```

**Key Files**:
- `engine/world.py` - Main simulation loop
- `engine/graphics_2d_pygame.py` - Rendering
- `engine/world_builder.py` - Vehicle/turret/engine/wheel definitions (weight, max_engine_force, rotation_speed, turret rotation_range, etc.)
- `ai/ai_human.py` - Human AI (task dispatch via `self.task_map`)
- `ai/ai_vehicle.py` - Vehicle physics (throttle/brake/wheel_steering, update_physics, rolling resistance by terrain, rotation gate)
- `ai/ai_human_vehicle_driver.py`, `ai/ai_human_vehicle_gunner.py`, `ai/ai_human_vehicle.py` - Crew role coordination
- `ai/ai_human_vehicle_crew_action.py` - VehicleCrewAction enum (DRIVING, ROTATING, WAITING_FOR_ROTATE, etc.)
- `engine/vehicle_diagnostics.py` - Vehicle debug screens

---

## Code Style

### Imports
```python
# import built in modules
import random
import copy
from enum import Enum

# import custom packages
from engine.graphics_2d_pygame import Graphics_2D_Pygame
import engine.math_2d
# import engine.something  # commented examples at end sometimes
```
- Grouped under "# import built in modules" then "# import custom packages". Absolute imports. No relative imports (except intra-dir). No `typing` or `from __future__`.

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
- Module headers: triple-quoted with "repo :" URL and notes section
- Inline comments used for explanations, section dividers, and notes (e.g. `# note - ...`)

---

## Key Conventions

### AI Task Dispatch
```python
self.memory["current_task"] = task_name
self.memory[task_name] = task_details
...
if self.memory["current_task"] in self.task_map:
    self.task_map[self.memory["current_task"]]()
```

### Vehicle/Magazine Access
```python
# Check ammo (in ai_human.py)
ammo_gun, ammo_inventory, magazine_count = self.check_ammo(weapon, vehicle)

# Compatible magazines: vehicle.ai.inventory + vehicle.ai.ammo_rack
# Filter by: magazine.is_gun_magazine and weapon.world_builder_identity in magazine.ai.compatible_guns
```

### Vehicle Crew Coordination (Driver / Gunner / ROTATING)
- Crew roles use `VehicleCrewAction` enum (`ai_human_vehicle_crew_action.py`).
- Key states for hull rotation: driver `ROTATING`, gunner `WAITING_FOR_ROTATE`.
- Loose coordination: each role reads the other's `memory["task_vehicle_crew"]["current_action"]`.
- Driver `action()` (runs frequently) mutates `vehicle.ai.throttle`, `brake_power`, `wheel_steering` directly.
- `action()` most frames; `think()` on `think_interval`.
- Rotation in `ai_vehicle.py` only applies if `current_speed > ~0.05` **or** `wheel_steering` is commanded. Combined with terrain `rolling_resistance_coeff` (0.3 on trees) and vehicle weight/engine force from world_builder, this commonly causes heavy casemates (Elefant etc.) to get stuck in ROTATING.
- Vehicles with narrow `rotation_range` on their turret (world_builder) depend heavily on this system.

### World Object Properties
- `is_vehicle`, `is_human`, `is_gun_magazine`
- `ai.inventory`, `ai.ammo_rack` (vehicles)
- `ai.projectiles` (magazine contents)
- `ai.projectile_type` (projectile categorization)

---

## Post-Edit Workflow
1. Lint: `pylint <file.py>` (from project root). Expect lots of pre-existing noise (imports, complexity, singleton comparisons). Use `--disable=import-error` and only look for *new* issues you introduced.
2. Syntax check: `python3 -m py_compile code/ai/your_file.py`
3. Smoke test: `bash start.sh --ai-test civilian 4` (or similar) — very effective for AI/vehicle physics changes.
4. Manual test: `bash start.sh` (or `cd code && python3 twe.py`). Use `~` for vehicle diagnostics when debugging throttle/brake/rotation states. Pay special attention to heavy vehicles and casemates on tree/vegetation tiles.

---

## Git
- `main`: stable, `dev`: active development
- **NEVER commit/push without explicit request**
