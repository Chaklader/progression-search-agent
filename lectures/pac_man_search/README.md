In this project, your Pacman agent will find paths through his maze world, both to reach a particular location and to collect food efficiently. You will build general search algorithms and apply them to Pacman scenarios.

You only need to modify search.py and searchAgents.py, and you only need to run autograder.py to complete the exercise. Full instructions are avialable here: http://ai.berkeley.edu/search.html

You can run all of the test cases on your code by opening a terminal and executing the command:

    $ python autograder.py

You can also run individual test cases by executing the command (you can replace "q1" with any of the choices q1-q8):

    $ python autograder.py -q q1

Notes:
---
- You can test your work as you progress using the autograder, however the grader only runs locally and YOU WILL NOT SUBMIT ANYTHING FOR THIS EXERCISE.

- The pacman.py script will animate your agent searching various domains (see commands.txt for instructions), but IT WILL NOT RUN IN THE WORKSPACE. You must download your code to run the GUI.

You can download your work by zipping the contents of the workspace and downloading the resulting file. Run the command:

$ zip -r search.zip *

Right click the file "search.zip" in the explorer bar on th e left side, then choose "download". NOTE: If you make changes to your code and want to download it again, run "rm search.zip" before regenerating the zip file.


COMMANDS
-------

Python autograder.py
python pacman.py
python pacman.py --layout testMaze --pacman GoWestAgent
python pacman.py --layout tinyMaze --pacman GoWestAgent
python pacman.py -h
python pacman.py -l tinyMaze -p SearchAgent -a fn=tinyMazeSearch
python pacman.py -l tinyMaze -p SearchAgent
python pacman.py -l mediumMaze -p SearchAgent
python pacman.py -l bigMaze -z .5 -p SearchAgent
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
python pacman.py -l bigMaze -p SearchAgent -a fn=bfs -z .5
python eightpuzzle.py
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs
python pacman.py -l mediumDottedMaze -p StayEastSearchAgent
python pacman.py -l mediumScaryMaze -p StayWestSearchAgent
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic 
python pacman.py -l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem
python pacman.py -l mediumCorners -p SearchAgent -a fn=bfs,prob=CornersProblem
python pacman.py -l mediumCorners -p AStarCornersAgent -z 0.5
python pacman.py -l testSearch -p AStarFoodSearchAgent
python pacman.py -l trickySearch -p AStarFoodSearchAgent
python pacman.py -l bigSearch -p ClosestDotSearchAgent -z .5 
python pacman.py -l bigSearch -p ApproximateSearchAgent -z .5 -q 
