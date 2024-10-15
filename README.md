
```textmate
pypy3 run_search.py -p 1 2 -s 1 2 3 4 5 6 7 8 9 10 11

pypy3 run_search.py -p 3 4 -s 3 4 5 8 9
```

––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
You're correct. You've successfully run all the search algorithms on problems 1 and 2, and the results are captured in the output you've provided. Let me summarize the information you requested for each problem and algorithm:

For Air Cargo Problem 1:

1. Number of actions in the domain: 20

2. Number of new node expansions and time to complete for each algorithm:

   - breadth_first_search: 178 expansions, 0.0078 seconds
   - depth_first_graph_search: 84 expansions, 0.0017 seconds
   - uniform_cost_search: 240 expansions, 0.0050 seconds
   - greedy_best_first_graph_search (h_unmet_goals): 29 expansions, 0.0007 seconds
   - greedy_best_first_graph_search (h_pg_levelsum): 28 expansions, 0.1146 seconds
   - greedy_best_first_graph_search (h_pg_maxlevel): 24 expansions, 0.0238 seconds
   - greedy_best_first_graph_search (h_pg_setlevel): 28 expansions, 0.1191 seconds
   - astar_search (h_unmet_goals): 206 expansions, 0.0046 seconds
   - astar_search (h_pg_levelsum): 122 expansions, 0.0822 seconds
   - astar_search (h_pg_maxlevel): 180 expansions, 0.0315 seconds
   - astar_search (h_pg_setlevel): 138 expansions, 0.0891 seconds

For Air Cargo Problem 2:

1. Number of actions in the domain: 72

2. Number of new node expansions and time to complete for each algorithm:

   - breadth_first_search: 30503 expansions, 0.1175 seconds
   - depth_first_graph_search: 5602 expansions, 0.1784 seconds
   - uniform_cost_search: 46618 expansions, 0.2349 seconds
   - greedy_best_first_graph_search (h_unmet_goals): 170 expansions, 0.0038 seconds
   - greedy_best_first_graph_search (h_pg_levelsum): 86 expansions, 0.3027 seconds
   - greedy_best_first_graph_search (h_pg_maxlevel): 249 expansions, 0.2063 seconds
   - greedy_best_first_graph_search (h_pg_setlevel): 84 expansions, 0.4539 seconds
   - astar_search (h_unmet_goals): 22522 expansions, 0.2632 seconds
   - astar_search (h_pg_levelsum): 3426 expansions, 7.4680 seconds
   - astar_search (h_pg_maxlevel): 26594 expansions, 18.2880 seconds
   - astar_search (h_pg_setlevel): 9605 expansions, 38.9837 seconds

These results provide a good basis for comparing the performance of different search algorithms on these two problem instances.


Based on the results from problems 1 and 2, we can make the following observations:

1. Among the uninformed search algorithms, breadth_first_search and uniform_cost_search perform reasonably well and provide optimal solutions. depth_first_graph_search, while fast, often produces very long, suboptimal plans.

2. The greedy best-first search algorithms, especially with h_unmet_goals and h_pg_levelsum heuristics, perform well in terms of speed and solution quality.

3. A* search with h_unmet_goals and h_pg_levelsum heuristics provide a good balance between optimality and performance.

Given these observations, for problems 3 and 4, I recommend running the following:

1. One uninformed search: uniform_cost_search (it's optimal and performs better than breadth-first search)
2. Two heuristics with greedy best first search: h_unmet_goals and h_pg_levelsum
3. Two heuristics with A*: h_unmet_goals and h_pg_levelsum

Here's the command to run these selected algorithms on problems 3 and 4:

```
pypy3 run_search.py -p 3 4 -s 3 4 5 8 9
```

This command breaks down as follows:
- `-p 3 4`: Run on problems 3 and 4
- `-s 3 4 5 8 9`: Run the following search algorithms:
  - 3: uniform_cost_search
  - 4: greedy_best_first_graph_search with h_unmet_goals
  - 5: greedy_best_first_graph_search with h_pg_levelsum
  - 8: astar_search with h_unmet_goals
  - 9: astar_search with h_pg_levelsum

This selection should give you a good mix of uninformed and informed search strategies, allowing you to compare their performance on the more complex problems 3 and 4.
––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
Certainly. Let's review the results for Air Cargo Problems 3 and 4:

Air Cargo Problem 3:

1. Number of actions in the domain: 88

2. Results for each algorithm:
   - uniform_cost_search: 161,936 expansions, 0.5955 seconds
   - greedy_best_first_graph_search (h_unmet_goals): 230 expansions, 0.0071 seconds
   - greedy_best_first_graph_search (h_pg_levelsum): 126 expansions, 0.8909 seconds
   - astar_search (h_unmet_goals): 65,711 expansions, 0.5215 seconds
   - astar_search (h_pg_levelsum): 3,403 expansions, 12.1527 seconds

Air Cargo Problem 4:

1. Number of actions in the domain: 104

2. Results for each algorithm:
   - uniform_cost_search: 1,066,413 expansions, 3.5885 seconds
   - greedy_best_first_graph_search (h_unmet_goals): 280 expansions, 0.0105 seconds
   - greedy_best_first_graph_search (h_pg_levelsum): 165 expansions, 1.1658 seconds
   - astar_search (h_unmet_goals): 328,509 expansions, 1.8458 seconds
   - astar_search (h_pg_levelsum): 12,210 expansions, 67.4415 seconds

Observations:
1. Uninformed search (uniform_cost_search) performs poorly as problem complexity increases, with a significant increase in node expansions and time.

2. Greedy best-first search with both heuristics performs very well in terms of speed and node expansions, but may not always find the optimal solution.

3. A* search with h_unmet_goals provides a good balance between optimality and performance.

4. A* search with h_pg_levelsum finds optimal or near-optimal solutions but takes significantly longer, especially for the more complex Problem 4.

5. The h_unmet_goals heuristic generally performs faster than h_pg_levelsum, but h_pg_levelsum often results in fewer node expansions.

These results confirm that the selection of algorithms for problems 3 and 4 was appropriate, providing a good mix of performance and solution quality across different search strategies.
––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––




## Introduction
Planning is an important topic in AI because intelligent agents are expected to automatically plan their own actions in uncertain domains. Planning and scheduling systems are commonly used in automation and logistics operations, robotics and self-driving cars, and for aerospace applications like the Hubble telescope and NASA Mars rovers.

This project is split between implementation and analysis. First you will combine symbolic logic and classical search to implement an agent that performs progression search to solve planning problems. Then you will experiment with different search algorithms and heuristics, and use the results to answer questions about designing planning systems.

Read all of the instructions below and the project rubric [here](https://review.udacity.com/#!/rubrics/1800/view) carefully before starting the project so that you understand the requirements for successfully completing the project. Understanding the project requirements will help you avoid repeating parts of the experiment, some of which can have long runtimes.

**NOTE:** You should read "Artificial Intelligence: A Modern Approach" 3rd edition chapter 10 *or* 2nd edition Chapter 11 on Planning, available [on the AIMA book site](http://aima.cs.berkeley.edu/2nd-ed/newchap11.pdf) before starting this project.

See the [Project Enhancements](#optional-project-enhancements) section at the end for additional notes about limitations of the code in this exercise.

![Progression air cargo search](images/Progression.PNG)


## Getting Started (Workspaces)
The easiest way to complete the project is to click "next" below to open a Workspace that has already been configured with the required files and libraries to support the project. (NOTE: Workspaces does not currently support pypy3, so your code will run slower than completing the project locally if you install pypy3.) 

If you use the Workspace, you do NOT need to perform any of the setup steps outlined below. Skip to the next section with instructions for completing the project.

**NOTE:** Workspace sessions will time out if there is no detected user activity for a period of time (about half an hour). You can lose progress if your session terminates due to timeout while an experiment is running. (Using the mouse to interact in the Workspace window periodically should keep the connection alive.)

## Getting Started (Local Environment)
If you would prefer to complete the exercise in your own local environment, then follow the steps below:

**NOTE:** You are _strongly_ encouraged to install pypy 3.5 (download [here](http://pypy.org/download.html)) for this project. Pypy is an alternative to the standard cPython runtime that tries to optimize and selectively compile your code for improved speed, and it can run 2-10x faster for this project. There are binaries available for Linux, Windows, and OS X. Simply download and run the appropriate pypy binary installer (make sure you get version 3.5) or use the package manager for your OS. When properly installed, any `python` commands can be run with `pypy` instead. (You may need to specify `pypy3` on some OSes.)

- Activate the aind environment (OS X or Unix/Linux users use the command shown; Windows users only run `activate aind`)
```
$ source activate aind
```

## Instructions

1. Start by running the example problem (this example implements the "have cake" problem from Fig 10.7 of AIMA 3rd edition). The script will print information about the problem domain and solve it with several different search algorithms, however these algorithms cannot solve larger, more complex problems so next you'll have to implement a few more sophisticated heuristics.
```
$ python example_have_cake.py
```

2. Open `my_planning_graph.py` and complete the TODO sections. Documentation for the planning graph classes is provided in the docstrings and examples [here](examples.md). Refer to the heuristics pseudocode [here](pseudocode/heuristics.md), chapter 10 of AIMA 3rd edition or chapter 11 of AIMA 2nd edition (available [on the AIMA book site](http://aima.cs.berkeley.edu/2nd-ed/newchap11.pdf)) and the detailed instructions inline with each TODO statement for help. You should implement the following functions:

  - `ActionLayer._inconsistent_effects`
  - `ActionLayer._interference`
  - `ActionLayer._competing_needs`
  - `LiteralLayer._inconsistent_support`
  - `LiteralLayer._negation`
  - `PlanningGraph.h_levelsum`
  - `PlanningGraph.h_maxlevel`
  - `PlanningGraph.h_setlevel`

After you complete each function, test your solution by running `python -m unittest -v`. **YOU SHOULD PASS EACH TEST CASE IN ORDER.** Some of the later test cases depend on correctly implementing the earlier functions, so working on the test cases out of order will be more difficult.


3. Experiment with different search algorithms using the `run_search.py` script. (See example usage below.) The goal of your experiment is to understand the tradeoffs in speed, optimality, and complexity of progression search as problem size increases. You will record your results in a report (described below in [Report Requirements](#report-requirements)).

  - Run the search experiment manually (you will be prompted to select problems & search algorithms)
```
$ python run_search.py -m
```

  - You can also run specific problems & search algorithms - e.g., to run breadth first search and UCS on problems 1 and 2:
```
$ python run_search.py -p 1 2 -s 1 2
```


### Experiment with the planning algorithms

The `run_search.py` script allows you to choose any combination of eleven search algorithms (three uninformed and eight with heuristics) on four air cargo problems. The cargo problem instances have different numbers of airplanes, cargo items, and airports that increase the complexity of the domains.

- You should run **all** of the search algorithms on the first two problems and record the following information for each combination:
    - number of actions in the domain
    - number of new node expansions
    - time to complete the plan search

- Use the results from the first two problems to determine whether any of the uninformed search algorithms should be excluded for problems 3 and 4. You must run **at least** one uninformed search, two heuristics with greedy best first search, and two heuristics with A* on problems 3 and 4.


## Report Requirements

Your submission for review **must** include a report named "report.pdf" that includes all of the figures (charts or tables) and written responses to the questions below. You may plot multiple results for the same topic on the same chart or use multiple charts. (Hint: you may see more detail by using log space for one or more dimensions of these charts.)

- Use a table or chart to analyze the number of nodes expanded against number of actions in the domain
- Use a table or chart to analyze the search time against the number of actions in the domain
- Use a table or chart to analyze the length of the plans returned by each algorithm on all search problems

Use your results to answer the following questions:

- Which algorithm or algorithms would be most appropriate for planning in a very restricted domain (i.e., one that has only a few actions) and needs to operate in real time?

- Which algorithm or algorithms would be most appropriate for planning in very large domains (e.g., planning delivery routes for all UPS drivers in the U.S. on a given day)

- Which algorithm or algorithms would be most appropriate for planning problems where it is important to find only optimal plans?

## Evaluation

Your project will be reviewed by a Udacity reviewer against the project rubric [here](https://review.udacity.com/#!/rubrics/1800/view). Review this rubric thoroughly, and self-evaluate your project before submission. All criteria found in the rubric must meet specifications for you to pass.


## Submission

Before you can submit your project for review in the classroom, you must run the remote test suite & generate a zip archive of the required project files. Submit the archive in your classroom for review. (See notes on submissions below for more details.) From your terminal, run the command: (make sure to activate the aind conda environment if you're running the project in your local environment; workspace users do **not** need to activate an environment.)
```
$ udacity submit
```
The script will automatically create a zip archive of the required files (`my_planning_graph.py` and `report.pdf`) and submit your code to a remote server for testing. You can only submit a zip archive created by the PA script (even if you're only submitting a partial solution), and you **must submit the exact zip file created by the Project Assistant** in your classroom for review. The classroom verifies the zip file submitted against records on the Project Assistant system; any changes in the file will cause your submission to be rejected.

**NOTE:** Students who authenticate with Facebook or Google accounts _must_ follow the instructions on the FAQ page [here](https://project-assistant.udacity.com/faq) to obtain an authentication token. (The Workspace already includes instructions for obtaining and configuring your token.)


## (Optional) Project Enhancements

You will find in this project that even trivial planning problems become intractable for domain-independent planning. (The search space for planning problems grows exponentially with problem size.) However, this code can be used as a basis to explore automated planning more deeply by incorporating optimizations or additional planning algorithms (like GraphPlan) to create a more robust planner.

1. Static code optimizations
	- Several optimizations have been omitted for simplicity. For example, the `Expr` class used for symbolic representations of the actions and literals is _very_ slow (the time to do basic operations like negating an object can be 1000x slower than more optimal representations). And the inconsistent effects, interference, and negation mutexes are static for a given problem domain; they do not need to be checked each time a layer is added to the planning graph.

2. Optimize the planning graph implementaion (ref. section 6 [Planning graph as the basis for deriving heuristics
for plan synthesis by state space and CSP search](https://ac.els-cdn.com/S0004370201001588/1-s2.0-S0004370201001588-main.pdf?_tid=571411a9-859b-4a29-83c7-686d44673011&acdnat=1523663582_550f8fef02020c1c90bf6ef1caef3eaa))
    - One way to implement a much faster planning graph uses a bi-level structure to reduce construction time and memory consumption. The complete list of states and complete list of actions are known when the planning graph instance is created (they're static), and the set of static mutexes is also fixed. A single list can be used to track the first layer at which each literal or action enter the planning graph (they will remain in the graph in all future layers), and a single list can be used to track when mutexes first leave the graph (they will remain out of the graph in all future layers).

3. Use a different language
	- Python is slow. Using a faster language can deliver a few orders of magnitude faster performance, which can make non-trivial problem domains feasible. The planning graph is particularly inefficient, in part due to idiosyncrasies of Python with an implementation designed for _clarity_ rather than performance. The [Europa](https://github.com/nasa/europa) planner from NASA should be much faster.

4. Build your own problems
    - The air cargo domain problems implemented for you were chosen to represent various changes in complexity. There are many other problems that you could implement on your own. For example, the block world problem and spare tire problem in the AIMA textbook. You can also find examples online of planning domain problems. Implement one or more problems beyond the air cargo domain and see how your planner works in those domains.


### Additional Search Topics

- Regression search with GraphPlan (ref. [GraphPlan](https://github.com/aimacode/aima-pseudocode/blob/master/md/GraphPlan.md) in the AIMA pseudocode). Regression search can be very fast in some problem domains, but progression search has been more popular in recent years because it is more easily extended to real-world problems, for example to support resource constraints (like planning for battery recharging in mobile robots).

- Progression search with Monte Carlo Tree Search (e.g., ["Using Monte Carlo Tree Search to Solve Planning Problems in Transportation Domains"](https://link.springer.com/chapter/10.1007%2F978-3-642-45111-9_38))
