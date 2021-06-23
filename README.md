# Flappybird-Multiplayer
Flappybird multiplayer game in python

<img src="https://raw.githubusercontent.com/mmax00/Flappybird-Multiplayer/master/preview.gif" width="694" height="313" />

A game is made in python using pygame library and sockets.

The way a server communicates with client:
1. Client sends server his name
2. Server sends client the state of a game (it can either be 'play' or 'q'-queue)
3. Server sends client info about the connected players
Then server will start clients thread for the rest of communication


Every time a client gets information from the server it checks for a few commands:
1. '/nc' - someone new has connected
2. '/dc' - someone has disconnected
3. '/f' - someone has pressed space so it needs to update birds flapping state
4. '/q' - update about number of queued players
5. '/s' - changes the state of the game
6. '/p' - information about pipes (their Y position; for example: /p*123*123*123*123*123*123*123*123*123*123*)


There could be a few improvements:
1. Server could constantly update clients about positions? (Right now it only updates when a client pressed space)
2. Better way to handle disconnects
3. Score system could be implemented

