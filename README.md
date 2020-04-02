# Flappybird-Multiplayer
Flappybird multiplayer game in python

A game is made in python using pygame library and sockets.

The way a server communicates with client:
1. Client send server his name
2. Server send client the state of a game (it can either be 'play' or 'q'-queue)
3. Server send client info about the connected players
Then server will start clients thread for the rest of communication

Every time a client gets information from the server it checks for a few commands:
'/nc' - someone new has connected
'/dc' - someone has disconnected
'/f' - someone has pressed space so it needs to update birds flapping state
'/q' - update about number of queued players
'/s' - changes the state of the game
'/p' - information about pipes (their Y position; for example: /p*123*123*123*123*123*123*123*123*123*123*)

There could be a few improvements:
*Server could constantly update clients about positions? (Right now it only updates when a client pressed space)
*Better way to handle disconnects
*Score system could be implemented

