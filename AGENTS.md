# AGENTS.md
## For agentic coding assistants operating in this TWE (To Whatever End) repository

This document provides essential commands, code style guidelines, and conventions for
this Python/Pygame-based WW2 tactical simulation game. TWE simulates individual
soldiers and vehicles with realistic physics, AI, and penetration mechanics.

No formal build system (no pyproject.toml, setup.py, or Makefile). Run directly with Python3.
No unit/integration tests (manual playtesting via `twe.py`). No CI/CD.

---

## Commands

### Running the Game
```
cd code/
python3 twe.py  # Launches main game loop (Graphics_2D_Pygame)
# Screen size hardcoded: (1920,1080) in code/twe.py:26
```
- Controls: WASD move, F fire, TAB context menu, ~ debug menu (README.md).
- Quick start: Main menu > Quick Battle > Civilian > 5k points.

### Installation/Dependencies
```
pip install pygame --user  # Only external dep (misc_notes/install_notes.txt)
# Platform notes:
# - Fedora: sudo dnf install python3-pip; pip install pygame --user
# - Windows: py -m pip install pygame --user
# - macOS: brew install python; pip3 install pygame --user
```
Data: `code/data/ingest.py` populates `data/data.sqlite` (names/projectiles).

### Linting & Static Analysis
No built-in linters. Use:
```
pip install pylint  # Recommended (used in tools/code_review.sh)
pylint code/engine/world.py  # Lint single file
pylint code/  # Lint all (slow on large files like ai_human.py ~2700 lines)
```
Code review script:
```
cd code/tools/
bash code_review.sh  # Runs external tool (~/localdev/review/code/review.py) on key files:
                     # world_builder.py, world.py, ai_human.py, ai_human_vehicle.py
alias r='python3 ~/localdev/review/code/review.py'  # From code_review.sh
r ../engine/world.py  # Review single file
```

### Type Checking
No mypy.ini or typing usage. Suggest:
```
pip install mypy
mypy code/  # Will fail (no annotations); use --ignore-missing-imports
```

### Testing
**No formal tests** (no pytest.ini, tests/, or test_*.py).
- Manual: Run `twe.py`, use debug menu (~), playtest battles.
- Data checks: `code/data/query_check.py` (dumps projectile_data).
- Profiling:
```
python3 -m cProfile -o profile.prof twe.py
pip install snakeviz --user
snakeviz profile.prof  # Visualize hotspots (e.g., grid_manager.update_world_objects)
```

### Asset/Tools
```
cd code/tools/
python3 image_tool.py  # Interactive sprite alignment (Pygame GUI for bounds/offsets)
python3 armor_thickness.py 20 60  # Calc effective thickness: 20mm @ 60° slope
```

### Git & Repo State
```
git status  # Untracked: art/ XC files, saves/
git log --oneline -10  # Recent: dev branch active (main stable)
git diff  # Staged/unstaged changes
# NEVER commit/push without user request. No hooks.
```

### Useful Searches (via tools)
```
glob \"**/ai/*.py\"  # AI modules (60+)
grep -r \"update_task\" code/ai/ai_human.py  # Task dispatch patterns
read code/engine/world.py  # Core sim loop (~970 lines)
```

**Post-Edit Workflow**:
1. Lint changed files: `pylint <file.py>`
2. Run game: `python3 twe.py` (check crashes/visuals).
3. No auto-typecheck/lint; manual verify.

---

## Code Style Guidelines

### Imports (Strict Grouping)
```
#import built in modules
import random
import copy
import threading

#import custom packages  # engine/, ai/
from engine.graphics_2d_pygame import Graphics_2D_Pygame
import engine.math_2d
from ai.ai_faction_tactical import AIFactionTactical
```
- **Order**: Builtins > locals (engine/ai). Absolute paths (90%+). No relative except intra-dir.
- **No typing/from __future__**. Avoid unused imports.

### Formatting (PEP8-ish, 4-space indent)
- **Indent**: 4 spaces (no tabs).
- **Lines**: <100 chars preferred; ~120 OK for conditionals.
- **Spacing**: 1 blank line funcs/classes; 2 post-imports/docstrings. No trailing WS.
- **Quotes**: Double for strings (`"error"`); single for keys (`'task_think'`).

### Naming Conventions
- **snake_case**: Vars/fns (`world_coords`, `update_task_engage_enemy`).
- **PascalCase**: Classes (`AIHuman`, `World`).
- **UPPER_SNAKE**: Globals/constants (`GRAVITY` inconsistent).
- **Abbreviations**: Lower (`ai`, `wo` for WorldObject).
- Old-style classes: `class AIHuman(object):` (migrate to `class AIHuman():`).

### Typing/Annotations
- **None**: No `typing.List`, `-> None`. Dynamic only (`self.memory = {}`).
- Add gradually: `from typing import Dict, Optional`; annotate new code.

### Error Handling
- **Minimal try/except**: Bare `except Exception:` for I/O/math. Prefer:
  ```
  engine.log.add_data('error', 'msg', True)  # Centralized logging
  print('Error: ...')  # Fallback
  ```
- No `raise`. Validate inputs early (`if obj is None: return`).

### Comments & Docstrings
- **Module Header**: Triple-quote top (repo, email, notes).
```
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : ...
'''
```
- **Inline**: `# note - ...` for TODOs/warnings.
- **Docstrings**: Sparse triple-quotes for classes (`'''world class...'''`); add for public methods.

### Class/Method Structure
- **AI/State**: `self.memory = {}` dict for tasks/state. Dispatch: `self.task_map['task_foo']()`.
- **Long Methods**: `update()` 100-500+ lines OK (AI dispatchers). Split if >300.
- **Inheritance**: Flat (`class AIHuman(object):`); composition (`self.in_vehicle_ai = AIHumanVehicle(self.owner)`).
- `__init__`: Sets 20-50 attrs. No `__slots__`/dataclasses.

### Patterns
- **Queues**: `add_queue`, `remove_queue` for world ops (thread-safe).
- **Events**: `handle_event(event, data)` dispatcher.
- **Coords**: `world_coords` lists `[x,y]`; `screen_coords`.
- **Globals**: Minimal; avoid.

### Security/Best Practices
- No secrets/keys. Pure sim (no net/DB beyond local SQLite).
- Physics: `engine.math_2d` utils (dist, rotation).
- NEVER add comments unless requested.

**Mimic Existing**: Check neighbors (`code/ai/ai_human.py` for AI tasks). Run `pylint` post-edit.

(152 lines total)