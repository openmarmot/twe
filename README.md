# twe
ww2 eastern front sim 

![screenshot](/screenshots/twe-feb-09-2020.png "boop")


TWE is short for 'To Whatever End' which was the title of a game I worked on from about 2007-2010.
The game was written in C# with the Microsoft XNA graphics framework and was going to be a open ended world war 2 eastern front simulation.
Sometime in 2010 I lost all the code due to a accidentally formatting the NAS where it was stored.



This repo is a fresh start at TWE using Python3 and Pygame. This time around I'm using 2d as I found making models and doing animation was a huge time 
sink on the old game that I didn't really enjoy. It is written completely from scratch based on my memory of previous game engines I've made. I will put reference notes in the code where possible when I copy significant code from the internet.

General Concepts
- fun comes from open world and emergent game play - game is not focused on player
  the focus is on 2 AI sides fighting eachother.
- eastern front roughly 1944-1945. roughly historical
- two modes : real time tactical environment and a map
- map size is not limited, each tile with be generated as needed
- not balanced on purpose. russian advantage as existed in the real life time period
- empasis on iron man mode. strategic game doesn't start over when player dies they just spawn again

Current State on Master branch
The game runs. There is basic movement for the user and a bot will turn to face you.


Check the changelog on the Dev branch to see what I've been working on.
  
To Play 
- install python3 and pygame
- download code
- python3 twe.py


License / Whatever
- I want to do this project completely by myself to improve my python skills and just as a fun hobby. 
- However - I put it on github for a reason. Feel free to copy code from it if you find it useful. If you use a lot of code I'd appreciate a little shout out or note as to where you got it. Thanks!
