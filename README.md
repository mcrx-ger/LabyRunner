> Welcome to LabyRunner - a game by mcrx-ger! 
>
> This is a game that trains your strategic-thinking and quick responses under stress. It is inspired by the book *The Will of the Many - James Islington*

# How to play

### Objective

The player's goal is to maneuver the red rectangle to an exit of the maze. He will always start in the middle of the Labyrinth.

### Rules

1. If the player is caught by one of the three enemies, the game is over. They are represented by the smaller grey rectangles. 
2. The opponents only appear when the radar reveals them, so keep your eyes open - this is essential for an overview! A radar will appear every 5 seconds.
3. The speed and intelligence of the opponents will depend on the difficulty you select.
4. As an compensation for this disadvantage, the player has the ability to manipulate some walls of the labyrinth, marked by their green color.

### Gameplay

- With Keyboard: 
    1. Steer the player with the arrow-keys.
    2. Select the walls with the "WASD"-keys. You can see which wall is currently selected by the small red point central to the each wall changing its color to red.
    3. If you want to manipulate a certain wall, you need to select it and then press SPACE. Now you can change the direction of the wall with "WASD" once every second.
    4. After changing the direction of a wall, press SPACE again. Now you are able to select other walls again.

- With Controller (**recommended** due to more accurate wall selection):
    1. Steer the player with the left joystick
    2. Select the walls with the right joystick.
    3. To manipulate a wall after selection, press RB. Then, change the direction with the right joystick.
    4. To select other walls after manipulating one, press RB again.

# Development

- This game has been coded with minimal use of AI (only for explanatory / debugging purposes).
- Key elements I am proud of are the minimax algorithm and the control mechanism of the walls.

### Minimax Algorithm

- A major challange was to make the algorithm fast and accurate. As of now, minimax works totally fine with depth 75+ due to an idea I had to maximize its speed while preserving the accuracy of the valuation function, called *metalists* (it's probably not a new trick, but I came to the concept all by myself) 
> see `make_metalists()`
- Since the minimax algorithm considers (almost) every possible movement of the player and the opps, *metalists* are snapshots of the current map that contain the distances of every field to every exit and every field to every other field. That way, *metalists* can be used in every iteration of the minimax (valuation) algorithm. Instead of calculating the distance of the player to the exit and the distance of the enemies to the player in every single iteration of the valuation function via BFS, they can now simply be updated when the walls of the maze change. They require only 338 BFS-searches through the maze.
> see `minmax_value()`
- Another measure to improve the efficiency of the minimax algorithm was a visited-list containing every visited node in the branch. This may not work in other use-cases of the algorithm, but in my case, moving to a field twice makes no sense for the enemies as they should be trying to cut the way of the player and catch him as fast as possible. 
> see `p_visited` and `o_visited` in `minimax()`

### Wall selection mechanism

- This mechanism has been optimised by utilizing two distinct values to choose the wall the user is most likely to mean 
1. Angle of the controller joystick compared to the angle of the currently selected wall to every other possible wall
2. Distance of the currently selected wall to every other possible wall
- The wall which has the least difference in angle and least distance will be the one the user wants to access. 
> see `search_closest_point()`
