# TWE 
WW2 Eastern Front Sim

TWE is short for 'To Whatever End' which was also the title of a game I worked on from about 2007-2010.
The original game was originally written in C# with the Microsoft XNA graphics framework and was going to be a open ended world war 2 eastern front simulation. Sometime in 2010 I lost all the code when I accidentally erased the NAS where it was stored. This repo is a fresh start (from scratch) at TWE using Python3 and Pygame. I've decided to switch from 3d to 2d so that I can make more progress on the interesting stuff without getting bogged down with modeling and animation.

TWE is a tactical wargame based roughly on the end of WW2. Unlike most war games the player only controls a single soldier, and the AI can do everything that the player can. The damage model works exactly the same for the player as it does for the AI, and the player has no advantages 
other than their brain.

I am developing this game by just randomly working on whatever I feel like on a particular day. This means that game development does not progress in any normal fashion and I often add small features that I can insert with a couple hours of work. Read the change_log in the dev branch to keep up with the latest progress. 

![screenshot](/screenshots/twe_panzer_iv.png "TWE screenshot")

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

![screenshot](/screenshots/su100_vehicle_diag_screen.png "Vehicle Diagnostics screen for Su100")

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
| German | Kubelwagen | Utility | unarmored light all terrain car | 
| German | Pak 40 | AT Gun | Towed gun |
| German | Panzer IV Ausf G | Tank | 75mm L43 |
| German | Panzer IV Ausf H | Tank | 75mm L48 |
| German | Panzer IV Ausf J | Tank | Minor differences from the H |
| German | Panzer VI Ausf E Tiger | Tank | Tiger 1 |
| German | Raupenschlepper OST (RSO) | Utility | tracked utility vehicle |
| German | RSO Pak | AT Vehicle | RSO with a Pak 40 |
| German | Sd.kfz.10 | Halftrack | unarmored prime mover |
| German | Sd.kfz.234/1 | AFV | Heavy recon car with a 2cm turret |
| German | Sd.kfz.234/2 Puma | AFV | 5cm turret |
| German | Sd.kfz.251/1 | APC | The famous German half-track |
| German | Sd.kfz.251/2 | APC | 8 cm mortar carrier |
| German | Sd.kfz.251/9 'Stummel' | AFV | 75mm L24 |
| German | Sd.kfz.251/9 Late | AFV | gains a MG |
| German | Sd.kfz.251/22 | AFV | Pak 40 |
| German | Sd.kfz.251/23 | AFV | has the 234/1 2cm turret |
| Soviet | Lend Lease American Truck | Utility | |
| Soviet | GAZ-61 | Utility | off-road staff car|
| Soviet | Su-85 | Tank | Basically a turretless T34-85 |
| Soviet | Su-100 | Tank | Better armor and gun than the Su-85 |
| Soviet | T20 'Komsomolets' | Utility | Armored Tractor |
| Soviet | T34-76 | Tank | A late model T34-76 |
| Soviet | T34-85 | Tank | |
| Soviet | T70 | Tank | light tank with a 45mm gun |
| Soviet | Zis 5 Trunk | Utility | |
| Soviet | 37mm AA Gun | AA | Towed gun. Can be used against infantry and light vehicles|


### A note on Infantry Weapons 
I already have a large amount of infantry weapons in game, but currently infantry weapons just don't matter much - the game is dominated by vehicle warfare. 


### Main branch is stable. Dev branch is the latest and may be less stable. Check the change_log for details. Dev is merged to Main when I feel like it.
  
### Install Instructions
Primarily developed on Fedora Linux
Occasionally tested on Windows and Mac

- install python3 and pygame
- download code
- change directory to the code directory
- python3 twe.py (windows would be: py twe.py)
- if you need to change the screen resolution, it is currently set in code/twe.py
- more notes in misc_notes/install_notes.txt

### Controls

#### General Controls  
| Key | Use |
|---|---|
| '[' | Zoom in | 
| ']' | Zoom out |
| 'space bar' | Toggle a circle that shows your weapon range | 
| 'tab' | Bring up a context menu or exit the current mehu |
| 'esc' | Exit the current menu | 
| 'left ctrl' | Take a screenshot (saves to code/game_screenshots) |
| '~' | Brings up the debug menue |
| 'm' | Toggles Map (colored pointers to world areas) |


#### Human (on foot) Controls
| Key | Use |
|---|---|
| 'w/s/a/d' | Movement | 
| 'f' | Fire primary weapon if equipped |
| 'g' | Throw grenade or other throwable item | 
| 't' | Fire antitank weapon if equipped |
| 'p' | Toggle prone | 
| 'r' | Reload your prmary weapon with a compatible magazine from your inventory |
| 'tab' | Human context menu |

#### Vehicle Driver Role Controls
| Key | Use |
|---|---|
| 'w' | Gas | 
| 's' | Brake |
| 'a' | Steer left | 
| 'd' | Steer right |
| 'tab' | Vehicle context menu |

#### Vehicle Gunner Controls
Note - enabling the vehicle HUD from the context menu is very useful if you are a driver or commander
| Key | Use |
|---|---|
| 'w' | Rotates the turret to aim where the mouse is (if possible) | 
| 's' | Fire coaxial weapon if equipped |
| 'a' | Rotates the turret counter-clockwise | 
| 'd' | Rotates the turret clockwise |
| 'f' | Fires main gun | 
| 'r' | Reloads whatever weapon is empty |
| 'tab' | Vehicle context menu |

#### Airplane Controls
Note that airplanes haven't been worked on recently and this code likely has issues
| Key | Use |
|---|---|
| 'w' | Elevator | 
| 's' | Elevator and brake if on the ground |
| 'a' | Aileron roll left | 
| 'd' | Aileron roll right |
| 'left arrow' | Throttle down | 
| 'right arrow' | Throttle up |
| 'tab' | Vehicle context menu |

### Getting Started 
From the main menu
- choose Quick Battle
- choose civilian faction
- choose 5k point random battle. This should run on most systems
- you will now spawn. your character is always in the center of the screen
- play around with movement, then use the debug menu ('~') to spawn in a vehicle
- walk up close to the vehicle, click on it, and choose 'enter vehicle'
- hit 'tab' to open the vehicle context menu. use the engine menu to start the engine
- use the '[' key to zoom out a bit and see if there are german or soviet troops near you
- observe the ai fighting over the towns
- use the debug menu to spawn in guns or tanks and try them out




![screenshot](/screenshots/twe_forest_battle.png "TWE screenshot")
This screenshot shows the end of a large battle in a forested area. 