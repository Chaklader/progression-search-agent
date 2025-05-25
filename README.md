# Air-Cargo Progression Search Planner

A classical AI planning agent that solves **Air-Cargo logistics** problems using **progression (forward) state–space
search**. The project is adapted from the Udacity _Artificial intelligence (AI)_ Nanodegree and implements several heuristic
functions based on **planning graphs** to guide the search.

<p align="center">
  <img src="images/Progression.PNG" alt="Progression air cargo search" width="500" height="auto">
</p>


---

##### Table of Contents

1. [Project Overview](#project-overview)
2. [Algorithms & Heuristics](#algorithms--heuristics)
3. [Repository Layout](#repository-layout)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Running Experiments](#running-experiments)
7. [Unit Tests](#unit-tests)
8. [Report Generation](#report-generation)
9. [Troubleshooting & FAQ](#troubleshooting--faq)
10. [Contributing](#contributing)
11. [License](#license)

---

##### Project Overview

The agent's task is to find a sequence of actions that transports cargo between a set of airports while obeying domain
constraints (loading/unloading cargo, flying planes, etc.). Each Air-Cargo problem instance differs in the number of
cargos, planes and airports, resulting in exponentially larger search spaces.

Your objectives in this repository are:

1. **Implement Planning-Graph heuristics** in `my_planning_graph.py`:
    - `h_levelsum`
    - `h_maxlevel`
    - `h_setlevel`
2. **Define mutex checks** for actions and literals.
3. **Compare uninformed and informed search algorithms** on four problem instances using `run_search.py`.
4. **Analyse the results** and summarise findings in `report.pdf`.

---

##### Algorithms & Heuristics

The planner can be paired with any of the search or heuristic combinations below (indices refer to the menu in
_run_search.py_):

| #   | Search Function                | Heuristic       | Optimal? |
| --- | ------------------------------ | --------------- | -------- |
| 1   | Breadth-First Search           | –               | Yes      |
| 2   | Depth-First Graph Search       | –               | No       |
| 3   | Uniform-Cost Search            | –               | Yes      |
| 4   | Greedy Best-First Graph Search | `h_unmet_goals` | No       |
| 5   | Greedy Best-First Graph Search | `h_pg_levelsum` | No       |
| 6   | Greedy Best-First Graph Search | `h_pg_maxlevel` | No       |
| 7   | Greedy Best-First Graph Search | `h_pg_setlevel` | No       |
| 8   | A\* Search                     | `h_unmet_goals` | Yes      |
| 9   | A\* Search                     | `h_pg_levelsum` | Yes      |
| 10  | A\* Search                     | `h_pg_maxlevel` | Yes      |
| 11  | A\* Search                     | `h_pg_setlevel` | Yes      |

The planning-graph heuristics are inspired by Russell & Norvig, _Artificial Intelligence – A Modern Approach_ (3rd ed.),
§10.3:

- **Level-Sum** – sum of the cost (graph level) at which each goal literal first appears.
- **Max-Level** – maximum single-goal level cost.
- **Set-Level** – first level in which all goals appear **and** none are pairwise mutex.

---

##### Repository Layout

```
.
├── air_cargo_problems.py   # Concrete Air-Cargo problem generators (P1–P4)
├── my_planning_graph.py    # TODO: implement graph heuristics here
├── run_search.py           # CLI for running experiments
├── planning_problem.py     # Abstract search problem definition (provided)
├── _utils.py               # Helper classes & functions (FluentState, encoding,…)
├── tests/                  # Unit tests executed by `python -m unittest -v`
└── README.md               # You are here ✔︎
```

> The project depends on the `aimacode` package (bundled in the _lectures_ directory) and requires **Python 3.8+**.

---

##### Installation

1. **Clone the repo**

```bash
$ git clone https://github.com/Chaklader/progression-search-agent.git
$ cd progression-search-agent
```

2. _(Optional but recommended)._ **Create a virtual-environment**

```bash
$ python -m venv venv
$ source venv/bin/activate        # Windows: venv\Scripts\activate
```

3. **You're all set!**  The project has **no external dependencies** beyond the Python standard library.
   The AIMA helpers (`aimacode`) are already included in `lectures/`, so you can skip any `pip install` step.

4. _(Optional)_ **Use PyPy 3** for a 2-10× speed-up:

```bash
$ brew install pypy3              # macOS example
$ pypy3 run_search.py -m          # run planner with PyPy
```

---

##### Quick Start

Run the solver interactively:

```bash
$ pypy3 run_search.py -m # can also use python but pypy is 2-10x faster
```

You will be prompted to pick 1…4 problems and one or more search algorithms.

Run _Problem 1_ with Uniform-Cost Search directly:

```bash
$ pypy3 run_search.py -p 1 -s 3
```

Run _Problems 1 & 2_ with Breadth-First and Greedy-Best-First (Level-Sum heuristic):

```bash
$ pypy3 run_search.py -p 1 2 -s 1 5
```

---

##### Running Experiments

The experiment script prints:

- plan length (number of actions),
- number of node expansions,
- search time.

You can run all problems (1-4) with selected search algorithms (3, 5, 9) directly like this:
```bash
$ pypy3 run_search.py -p 1 2 3 4 -s 3 5 9
```

Use this data to populate tables/figures for your **report**. For reproducible timing results, `pyperf` is recommended (as `timeit` can be unreliable for scripts):

First, install `pyperf` using PyPy's pip if you haven't already:
```bash
$ pypy3 -m pip install pyperf
```

For a quick timing check (one warm-up, one measured run on a single problem/search):
```bash
$ pypy3 -m pyperf command -w 1 -n 1 -l 1 -- python run_search.py -p 1 -s 3
```

For a faster benchmark using `pyperf`'s fast mode (fewer warm-ups/samples across a subset of problems/searches):
```bash
$ pypy3 -m pyperf command --fast -- python run_search.py -p 1 2 -s 3 5
```

For a comprehensive benchmark (this is the most thorough but may take several minutes):
```bash
$ pypy3 -m pyperf command -n 3 -l 1 -- python run_search.py -p 1 2 3 4 -s 3 5 9
```

Note: The full benchmark can take a significant amount of time to complete as it runs multiple problems with multiple search algorithms, each repeated several times by `pyperf`.

---

##### Unit Tests

Ensure your implementation passes all tests **before** running large experiments:

```bash
$ pypy3 -m unittest -v
```

A green test-suite implies that the heuristics/mutex logic in `my_planning_graph.py` is likely correct.

---

## Report Generation

Create `report.pdf` containing:

1. Tables/plots of **nodes expanded vs. domain size** and **search time vs. domain size**.
2. Plan lengths for every algorithm/problem combination.
3. Answers to the three analysis questions listed in this README.

Include any scripts/notebooks you used to generate plots in a `/notebooks` or `/analysis` folder (optional).

---
