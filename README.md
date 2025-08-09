# TWE 
WW2 Eastern Front Sim

TWE is short for 'To Whatever End' which was also the title of a game I worked on from about 2007-2010.
The original game was originally written in C# with the Microsoft XNA graphics framework and was going to be a open ended world war 2 eastern front simulation. Sometime in 2010 I lost all the code when I accidentally erased the NAS where it was stored. This repo is a fresh start (from scratch) at TWE using Python3 and Pygame. I've decided to switch from 3d to 2d so that I can make more progress on the interesting stuff without getting bogged down with modeling and animation.

TWE is a tactical wargame based roughly on the end of WW2. Unlike most war games the player only controls a single soldier, and the AI can do everything that the player can. The damage model works exactly the same for the player as it does for the AI, and the player has no advantages 
other than their brain.

I am developing this game by just randomly working on whatever I feel like on a particular day. This means that game development does not progress in any normal fashion and I often add small features that I can insert with a couple hours of work. Read the change_log in the dev branch to keep up with the latest progress. 

![screenshot](/screenshots/twe-oct-22-2024.png "TWE screenshot")

### General Concepts
- eastern front around 1944-1945. roughly historical
- two modes : real time tactical environment and a strategic map
- strategic map size is not limited, each tile with be generated as needed
- not balanced on purpose. russians should inevitably push the germans west
- vehicle / armor / weapon values are based on the actual real world values and not on perceptions of how things should be or modified for fun/balance.
- everything is simulated as much as possible, including individual bullets in magazines.
- emphasis on iron man mode. strategic game doesn't start over when player dies they just take over a new bot

### Armor Penetration System

I am aiming to have a armor penetration system that generates understandable repeatable results that 
simulate real world results as accurately as possible for a real time 2d game.  

Every projectile fired from a gun in the game is fully simulated with a visible object that has its own collision.  The result of firing the gun is not pre-calculated, it just depends on what the projectile runs into.  

Vehicles generally have several sections that can be hit 
- vehicle body : the lower portion of the vehicle 
- passenger compartment : the upper portion of the vehicle
- wheels
- turret(s) : the side of the vehicle that the turret is mounted on is also considered

Each side of a vehicle section has a value for 
- armor thickness 
- angle of armor (0 being vertical armor)
- armor thickness for any spaced armor (mostly German armor skirts)

When a projectile hits a vehicle the following is assessed
- The side of the vehicle that is hit
- THe affect of any spaced armor
- The affect of the armors angle on its calculated thickness
- The affect of the angle between the projectile and the armor on the armor thickness

Vehicles do not have a health value. Instead each vehicle section has unique damage effects.  
A projectile that does not penetrate has a chance to richochet off and hit something else.  

Hit data is saved and can be viewed with green and orange arrows showing hits through a debug menu option.  

### Things to do
- spawn different objects with the debug menu
- spawn as a german or russian and lead your squad into combat
- spawn as a civilian and try to survive the cross fire
- explore in a kubelwagen or a bicycle
- check cupboards for the elusive pickle jar item. eat pickles!
- check out the (very early) campaign mode

### Current List of Vehicles Simulated

| Faction | Name | Type | Notes |
|---|---|---|---|
| Civilian | Red Bicycle | Bike | |
| German | Fa223 Drache | Helicopter | |
| German | Jagdpanzer 38t 'Hetzer' | Tank | |
| German | Ju 88 | Airplane | |
| German | Kubelwagen | Utility | Also available in a camo version | 
| German | Pak 40 | AT Gun | |
| German | Panzer IV Ausf G | Tank | 75mm L43 |
| German | Panzer IV Ausf H | Tank | 75mm L48 |
| German | Panzer IV Ausf J | Tank | Minor differences from the H |
| German | Raupenschlepper OST (RSO) | Utility | tracked utility vehicle |
| German | RSO Pak | AT Vehicle | RSO with a Pak 40 |
| German | Sd.kfz.251/1 | APC | The famous German half-track |
| German | Sd.kfz.251/2 | APC | 8 cm mortar carrier |
| German | Sd.kfz.251/9 'Stummel' | AFV | 75mm L24 |
| German | Sd.kfz.251/9 Late | AFV | gains a MG |
| German | Sd.kfz.251/22 | APC | Pak 40 |
| Soviet | Lend Lease American Truck | Utility | |
| Soviet | Su-85 | Tank | Basically a turretless T34-85 |
| Soviet | Su-100 | Tank | Better armor and gun than the Su-85 |
| Soviet | T20 'Komsomolets' | Utility | Armored Tractor |
| Soviet | T34-76 | Tank | A late model T34-76 |
| Soviet | T34-85 | Tank | |
| Soviet | 37mm AA Gun | AA | |




### Main branch is stable. Dev branch is the latest and may be less stable. Check the change_log for details. Dev is merged to Main based on how buggy it is.
  
### To Play 
- install python3 and pygame
- download code
- change directory to the code directory
- python3 twe.py (windows would be: py twe.py)
- tested on Windows 10, Linux, Apple (M2)

### Controls
See gameplay_instructions.txt for a full list
- '~' opens/closes debug menu 
- 'w/s/a/d' movement
- left click on a object to open context menu
- tab close the active menu or open a player context menu
- 'esc' to exit menu
- 1-0 number keys are used in menus
- 'f' to fire weapon (if you have one)
- 'g' throw grenade (if you have one)
- 't' launch panzerfaust (if you have one)
- '[' zoom out
- ']' zoom in 





![screenshot](/screenshots/twe-mar-26-2025.png "TWE screenshot")
In this screenshot a large battle unfolds between Soviet and German forces. 