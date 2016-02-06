# web-bounty-swu-ake
SWU's bounty snake for 2016.

# overview
There are two types of nodes in this system: web and worker. The web node is a simple web server, and does not of the game state processing. When a game is started/ended/moved it updates redis appropriatly. Redis dictates what work needs to be and has been done.
The workers visit game states and evaluate them. If they find a better game state, they update a global variable for this, that the web server and other workers may check.




