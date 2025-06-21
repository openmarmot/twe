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
- emphasis on iron man mode. strategic game doesn't start over when player dies they just take over a new bot

### Things to do
- spawn different objects with the debug menu
- spawn as a german or russian and lead your squad into combat
- spawn as a civilian and try to survive the cross fire
- explore in a kubelwagen or a bicycle
- check cupboards for the elusive pickle jar item. eat pickles!
- check out the (very early) campaign mode

### Current List of Vehicles Simulated
- German Kubelwagen
- German Raupenschlepper OST (RSO) tractor
- German RSO PAK
- German Panzer IV Ausf G
- German Panzer IV Ausf H
- German Panzer IV Ausf J
- German Jagdpanzer 38t "Hetzer"
- German Ju88 bomber
- German FA223 Drache helicopter
- German Sd.kfz.251
- German Sd.kfz.251/22
- German PAK 40
- Soviet T20 "Komsomolets" armored tractor
- American/Soviet Lend-Lease truck
- Soviet T34-76 (late)
- Soviet T34-85
- Soviet SU-85
- Soviet 37mm AA gun
- Civilian Red Bicycle

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