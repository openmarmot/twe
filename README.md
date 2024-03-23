# TWE 
WW2 Eastern Front Sim

TWE is short for 'To Whatever End' which was the title of a game I worked on from about 2007-2010.
The game was originally written in C# with the Microsoft XNA graphics framework and was going to be a open ended world war 2 eastern front simulation.
Sometime in 2010 I lost all the code when I accidentally erased the NAS where it was stored. This repo is a fresh start (from scratch) at TWE using Python3 and Pygame. I've decided to switch from 3d to 2d so that I can make more progress on the interesting stuff without getting bogged down with modeling and animation.

I am developing this game by just randomly working on whatever I feel like on a particular day. This means that game development does not progress in any normal fashion and I often add small features that I can insert with a couple hours of work. Read the change_log in the dev branch to keep up with the latest progress.

![screenshot](/screenshots/twe-may-23-2021.png "TWE screenshot")


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


### Main branch is stable. Dev branch is the latest and may be less stable. Check the change_log for details.
  
### To Play 
- install python3 and pygame
- download code
- change directory to the code directory
- python3 twe.py (windows would be: py twe.py)
- tested on Windows 10, Linux, Apple (M2)

### Controls
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


### License / Whatever
- I want to do this project completely by myself to improve my python skills and just as a fun hobby. 
- However - I put it on github for a reason. Feel free to copy code from it if you find it useful. If you use a lot of code I'd appreciate a little shout out or note as to where you got it. Thanks! 
- On this project it is rare that I copy code from the internet, almost all of it is from scratch (that is why the math is so bad) - 
but when I have copied code I will try to include references from where I got it
