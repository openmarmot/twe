# Object Definition Conversion Issues
## old_object_definitions.py → code/engine/object_defs/

Generated from direct comparison of every registered key in object_defs/ against the corresponding `elif object_type == "..."` (or initial `if`) blocks in old_object_definitions.py (2026-06-20).

Focus: **completeness** of the port. Only items where the new `.py` is missing code/logic/values that existed in the old block, or where the object has no corresponding new file at all.

---

## 1. Objects with NO new file / registration (old had full definitions)

These will cause "Spawn Error" or silent failure when referenced (via add_standard_loadout, direct spawn, or legacy lists).

**Guns + Magazines**
- stg44 (gun)
- stg44_magazine
- ppsh43 (gun)
- ppsh43_magazine
- ptrs_41 (gun)
- ptrs_41_magazine

**Humans (specialized loadouts)**
- german_mechanic
- german_fg42-type2 (or fg42_type2 variant)
- german_stg44_panzerfaust
- german_stg44_panzerfaust_100
- soviet_svt40_sniper

**Engines**
- chrysler_flathead_straight_6_engine (check if still referenced anywhere)

**Count**: 13 (set-diff) + warehouse nuance (see below).

---

## 2. Files that exist but are incomplete / truncated / contain errors

### Vehicles (highest impact – physics, mobility, crew, ammo)

**german_sd_kfz_10_base.py** (and all users: german_sd_kfz_10, german_sd_kfz_10_camo)
- Old (2171-2253): full base with driver+passenger, all armor, **max_speed=385.9**, max_offroad, rotation_speed=40, collision=100, 5 bounding_circles, weight=4900, drag=0.9, frontal=5, fuel_tank (vol=114 + fill gas_80), maybach_hl42_engine + exhaust, battery_vehicle_6v, add fuel_can + random medical + random consumables + conditional panzerfaust_60, rotation random, min_wheels_front=1 rear=5, max_wheels=18, 1 front L/R + 8× rear L + 8× rear R (251_wheel).
- New: only crew + armor dicts. **Everything else missing**. Variants inherit nothing usable.

**german_sd_kfz_251_1.py**
- Old (2778+): adds 9 passengers (specific positions + 90/270 rotations) + 11× mg34_drum_magazine + conditional AP belt.
- New: only driver/gunner/commander/assistant + 10 mg34_belt + 1 conditional belt. **Passengers and drum count missing**.

**german_rso.py**
- Old: max_wheels=8 + `for b in range(2):` append 2× per corner (8 wheels).
- New: max_wheels=4 + one wheel per corner only.

**german_rso_pak.py**
- Old (2064-2163): ends with min/max_wheels + `for b in range(2)` wheel appends.
- New: cuts off after rotation_angle. **Wheel setup missing**.

**german_kubelwagen.py** (+ soviet_gaz_61.py)
- Multiple value + logic diffs:
  - Passengers: new ~2 total vs old 1 driver + 3 passengers.
  - collision/bounding: new 80 + 2 circles vs old 50 + 4 precise.
  - weight: 1500/1650 vs 725/1200.
  - drag/frontal, exhaust offsets, spare wheels (new max=0, old=1 + append), random inventory contents + timing.
- Camo thin wrapper is ok, but base data wrong.

**Bicycles** (german_military_bicycle.py, red_bicycle.py)
- Old: pedals engine, 2 wheels (front L/R), open_top, random panzerfaust60 + mg belt, different stats.
- New: incomplete wheel/engine/random/stats.

**german_smg42.py**
- Old: full carriage with driver/gunner/commander, pedals, speeds, ammo_rack + belts, max_wheels=0, open_top.
- New: almost empty (just gunner + basic stats).

**Mortars** (german_8cm_mortar.py, soviet_82mm_mortar.py)
- Old: 3 crew roles + seats, pedals engine, ammo_rack + 30 GrW, speeds/bounds/weight.
- New: minimal gunner only.

**german_pak40.py**
- Old: armor, 3 crew+seats, is_towed_gun, pedals, ammo_rack (20+10), wheels (incl rear).
- New: stripped down.

**soviet_37mm_m1939_61k_aa_gun_carriage.py**
- Similar omissions (roles, engine, rack, rear wheels, flags).

**Planes**
- german_fa_223_drache.py: missing is_airplane, stall/accel/climb/throttle flags, multiple rotors setup, extra fuel/engine/battery.
- german_ju88.py: missing mg + drums, 4 fuel tanks, 2 engines, is_airplane etc.

**german_jagdpanzer_38t_hetzer.py**
- Armor values, no radio_operator role, ammo_rack count, wheel min/max, image names, offsets differ.

**222 / 234 / some 251 variants**
- Frequently missing the post-crew ammo_rack_capacity + AP/HE magazine population loops for the main gun (present in old after the visible roles).

### Weapons (Guns / Magazines / Throwables)

- **All magazine files** (~43): continue to use `["stg44_magazine"]` sprite (inherited from old, but noted as universal placeholder).
- svt40_magazine.py: missing `removable = True` (old had it).
- mosin_magazine.py: missing `removable = False`.
- 2cm_kwk38_l55_magazine.py: missing `disintegrating = True`; projectile list differs.
- 45mm_19k.py (gun): missing `reload_speed`; range 1500 vs old 4000.
- Many cannon guns (2cm_kwk38, 5cm, various 75/76/85/88/100mm): missing mechanical_accuracy_deg, rotation=0, different rof/range/reload/type vs old. (Some may be intentional; many look like partial ports.)

### Humans

- civilian_man.py: **broken** – `z.name = engine.world_builder.engine.name_gen.get_name("civilian")` (double `.engine`). All other humans correctly do `import engine.name_gen`.
- civilian_shovel_man.py: old added german_field_shovel + 2× bandage + 2× random consumables_common. New only has coffee_tin + folding_shovel.

### Terrain (copy-paste name errors – wrong in old and still wrong)

- wood_quarter.py: `z.name = "wood_log"` (should be wood_quarter).
- terrain_mottled_transparent.py + ground_cover.py: `z.name = "ground_dirt_vlarge"`.

### Vehicle Turrets & Wheels (logic + file layout)

- remote_mg34_turret.py: missing `small=True`, `remote_operated=True`; turret_accuracy wrong, armor all zero, wrong sight optic.
- jagdpanzer_38t_main_gun.py: armor too low, position_offset wrong, rotation_range too narrow (-5/5 vs -20/20), gun id string, smoke offset.
- **Misplaced files**:
  - vehicle_wheels/ba_64_turret.py (registers "ba_64_turret")
  - vehicle_wheels/elefant_turret.py (registers "elefant_turret")
  These belong in vehicle_turrets/.
- fa_223_rotor.py: missing `is_rotor = True`; sprite/name differ from old rotor block.
- Several wheels have expanded compat lists or added armor (251, t34, pak, panzer38t) – may be improvements or drifts.

### Buildings

- warehouse.py: fully present with bounding circles. Old used an initial `if object_type == "warehouse"` (not elif), so it was easy to miss during grep extraction. Confirm intent.

---

## 3. Other / Minor

- Some new wheel/turret/vehicle files use slightly different numbers (weights, armor, compat, offsets) than old. These are listed only when the difference is large or structural (e.g. missing loops/roles).
- "warehouse" is the only registration in new with no direct old elif (because it was the first `if`).
- No widespread issues in: consumables (excellent), containers, effects, most optics, batteries, human_wearable, vehicle_engines, components, or the majority of detailed tank turrets (panzer_iv, tiger, t34, su, elefant etc.).

---

## Quick Reference: How the Comparison Was Done
- Extracted 352 keys from old via `grep -o 'elif object_type == "...'`.
- Extracted 340 registered keys from all `@register_object("...")` under object_defs/.
- Diff + manual block reads (full `create()` vs full old elif up to next object).
- Sub-category spot-checks + full reads on all vehicles, guns/mags, humans, and representatives from every other dir.

## Recommended Fix Order (impact)
1. sd_kfz_10_base + dependents (vehicles dead otherwise).
2. Missing stg44 / ppsh43 / ptrs_41 guns + mags + affected humans.
3. RSO, kubel/gaz, bicycles, mortars, pak40, smg42, aa carriage, fa223, ju88, hetzer.
4. 251/234/222 ammo_rack loops + passengers.
5. Human name bug + shovel man.
6. Terrain name bugs.
7. Turret/wheel logic + move misplaced files.
8. Review cannon gun param diffs.

Use `bash start.sh --ai-test civilian 4`, `~` debug, and `python3 -m py_compile` + pylint after edits (see AGENTS.md).

---

**End of report.** All data derived strictly from side-by-side reads of the two sources on 2026-06-20.
