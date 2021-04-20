# TWE 
WW2 Eastern Front Sim

TWE is short for 'To Whatever End' which was the title of a game I worked on from about 2007-2010.
The game was originally written in C# with the Microsoft XNA graphics framework and was going to be a open ended world war 2 eastern front simulation.
Sometime in 2010 I lost all the code when I accidentally erased the NAS where it was stored. This repo is a fresh start (from scratch) at TWE using Python3 and Pygame. I've decided to switch from 3d to 2d so that I can make more progress on the interesting stuff without getting bogged down with modeling and animation.

I am developing this game by just randomly working on whatever I feel like on a particular day. This means that game development does not progress in any normal fashion and I often add small features that I can insert with a couple hours of work. For example before writing this I added in several types of cheese - just for fun.

![screenshot](/screenshots/twe-ju88.png "ju88")


### General Concepts
- eastern front around 1944-1945. roughly historical
- two modes : real time tactical environment and a strategic map
- strategic map size is not limited, each tile with be generated as needed
- not balanced on purpose. russians should inevitably push the germans west
- emphasis on iron man mode. strategic game doesn't start over when player dies they just take over a new bot

### Things to do
- spawn objects and zombies with the debug menu
- try out different weapons on some helpless zombies 
- find and eat all four types of cheese


### Check the changelog on the Dev branch to see what I've been working on.
  
### To Play 
- install python3 and pygame
- download code
- python3 twe.py (windows would be py)

### Controls
- '~' opens/closes debug menu (spawn zombies!)
- 'w/s/a/d' movement
- left click on a object to open context menu
- 'esc' to exit menu
- 'f' to fire weapon (if you have one)
- 'g' throw grenade (if you have one)


### License / Whatever
- I want to do this project completely by myself to improve my python skills and just as a fun hobby. 
- However - I put it on github for a reason. Feel free to copy code from it if you find it useful. If you use a lot of code I'd appreciate a little shout out or note as to where you got it. Thanks!
