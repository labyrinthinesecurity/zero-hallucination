## A Proof of concept

Now that we are three years into the generative AI revolution, some patterns are emerging around how to approach AI safety. One of the most promising directions is hybrid AI: combining the strengths of Large Language Models (LLMs), which provide intuitive and adaptive answers, with symbolic AI (symAI), which ensures those answers are consistent, verifiable, and free from hallucinations.


There are many possible forms of hybridization. In this article, I’ll introduce one such design that I’ve tested in a proof of concept: the real-time Digital Twin. As you’ll see, it holds a lot of promise.


The first part of this article covers concepts & design. The second part provides an implementation: a fully functional proof of concept. The third and last part expands the concept to a real time situation.

## Part 1: Concepts and design

### What is a Digital Twin?

A Digital Twin (DT) is a concept borrowed from industry, where it describes a live digital replica of a complex physical system. In manufacturing, for example, thousands of sensors feed telemetry into a digital model that evolves in real time alongside the actual machine. A feedback loop ensures the DT behaves as faithfully as possible to the physical process.


But DTs need not be limited to physical systems. When delegating a business process to an AI agent, we can also construct a DT—a large state machine that encodes the global constraints of the process: business rules, regulations, exceptions, and so on.


The DT acts as a gatekeeper between the decision maker (the LLM) and the live environment: 

- any decision taken from the LLM is first validated against the DT by a symbolic AI before being passed on to live systems, to ensure all business rules are met
- conversely, any change occurring in the live system is transmitted to the DT so that it remains a faithful replicate at all times.

### Rules encoding
Global constraints are built from a corpus of automated reasoning (SMT) rules describing the process in machine-readable format, for the symbolic AI. Building this "by hand" is tedious, so tools like AWS Automated Reasoning for Bedrock can help derive constraints automatically from structured or unstructured documents.


Global constraints make up the default, "factory settings" of the DT.

### The genAI-SymAI Interaction

Here’s how the interaction works:

- At t=0, when the process begins, the AI agent is notified of the business rules, in natural language. It is asked to produce an initial plan version 0 (v0) a sequence of actions in JSON.
- This plan is ingested into the DT as a local constraint. Unlike global constraints, local ones are temporary and tied to the current problem.
- The symbolic AI verifies whether v0 + the global constraints as a whole is satisfiable
- If not, symbolic AI produces a root cause of the problem, technically known as an UNSAT core
- Agent is asked to update its plan based on UNSAT core analysis

### From Static Rules to Real-Time Updates
Unlike a static ruleset, a real-time DT is dynamic. It can ingest events that add, modify, or relax constraints as the process unfolds. At each tick t, the DT updates to reflect ground truth. Not just DT, but DT(t).


If an event occurs en-route (say, at time t=7) that invalidates plan v0, DT gets updated from environment sensors. The symAI is informed and runs a stepwise proof from t=0 to t=7 which invalidates plan v0 at t=7 and reports a new UNSAT core.


At this point, the agent is asked to propose a fix. Instead of starting over, it aims to find a minimal workaround, quickly patching the plan without overloading the LLM’s memory.


This sets up a tight feedback loop:

- The LLM proposes an updated plan (v1, v2 … vN).
- The symbolic AI verifies it against DT(7).
- If UNSAT, the process repeats until a valid solution is found.

## Part II: Proof of Concept
### Introducing "Torus bots"
Our PoC evaluates a hybrid AI approach combining a Large Language Model (Deepseek without chains-of-thoughts, to speed-up decisions) with a symbolic solver (Z3 SMT) to plan paths for multiple tethered robots on a toroidal grid. 


### Experimental Setup
Grid size: 30×30 torus
Number of robots: 10 (BotA…BotJ)
Path length: Start and goal positions ~10 cells apart
Time horizon: Adjustable, enough to allow straight-line paths
Constraints: Tethers collision avoidance (incuding self), continuous motion (robots cannot stop except when they reach their goal), wrap-around torus movement, and obstacles
The live environment is not implemented (with run a proof-of-concept, no actual bots are involved)

### A note on pathfinding
Some readers might claim, rightfully, that there are powerful algorithms out there (like A-star) that solve pathfinding problems much more efficiently than a LLM or a SMT. This, however, dismisses the reality of our robotic environment: 


- Robots may have defects affecting their motion law (eg: when bot Charly goes DOWN, DOWN and LEFT, then it actually performs a DOWN, DIAGONAL motion).
- We may want to add constraints related to the topology of the environment: recall that bots operate on a torus, not a square. We may want to ensure that tethers don't get entangled with the donut shape.
- We may add specific, tether related constraints (they may be passable under certain conditions)
 
The more constraints we add, the more symbolic AI will shine and the less pathfinding algorithms are likely to adapt.

### Methodology
We follow the methodology described in Part I:

- We initialize the DT with business rules encoded as global constraints. 
- Deepseek then proposes an initial plan (v0) based on the start and goal positions and intuitive pathing. 
- Z3 validates the plan against the constraints. 
- If the plan is UNSAT, the LLM generates an updated plan (v1, v2 …) iteratively until a SAT solution is found. 


We record both the number of iterations and the total computation time.

### Business rules encoding
Here are the rules governing Torus Bots, in natural language:

```
Task: 
Generate a 10-robots (named 'BotA', ..., 'BotJ') movement plan on a 30x30 toroidal grid over T timesteps. (set T as you see fit).
Since the number of constraints is huge, don't try to check. Use your intuition to find a heuristic, submit a plan (JSON generated by a python function that I wil run) and I will let my SMT solver check if it is satisfiable, then you can iterate based on the UNSAT cores the SMT found (if any).

Grid coordinates: 
(0,0) is bottom-left, (29,29) is top-right. Wraparound applies at edges: moving right from x=29 goes to x=0, moving up from y=29 goes to y=0.

Start and goal positions of the i-th bot:
- Start: (x=0,y=2*i)
- Goal: (x=10,y=2*i+1)

Rules:
1. **Movement:** Each robot moves exactly 1 step per timestep in one of the four cardinal directions (up/down/left/right), possibly wrapping around the grid edges.
2. **Self-avoidance:** Robots cannot occupy the same cell they occupied at any timestamp, except if they have reached their goal (in this case, and only in this case, they can just "sit there").
3. **Collision avoidance:** Robots cannot occupy the same cell as any other robot. This applies at **every timestep**, including start and goal positions.
4. **Continuous motion**: robots must keep moving until they reach their goal. Then, they can "sit there".
5. **No Idling**: at least one bot must not sit at goal, except at final timestep where of course all bots sit there.

Output format: Choose a T (any value you see fit) and JSON mapping robot names to a list of positions at each timestep from 0 to T-1.

Example valid JSON plan for 2 bots on 5x5 torus (commented, for structure reference only) for 8 timesteps from 0 to 7:
# {
#     'BotA': [(0,4), (4,4), (3,4), (2,4), (1,4), (1,3), (1,2), (2,2)],
#     'BotB': [(2,0), (2,1), (1,1), (1,2), (1,3), (2,3), (3,3), (3,2)]
# }
 Here is another valid plan for 2 boyd on 5x5 torus where 'BotB' is allowed to "sit there" while BotA continues
# {
#    'BotA': [(0,4), (4,4), (3,4), (2,4), (1,4), (1,3), (1,2), (2,2)],
#    'BotB': [(2,0), (2,1), (3,1), (3,2), (3,2), (3,2), (3,2), (3,2)]
# }
```

We translate these rules into Z3 constraints: this is the most difficult part, but luckily it is a one shot operation.
These rules are all available in file symAI.py

### Deepseek's initial plan (V0)
We then submit the task to Deepseek. After a few seconds of thinking, Deepseek's initial JSON plan is returned as a python code generator (it can be found in file v0.deepseek_planner.py)


We run the code locally and upload the resulting JSON file, v0.json, to symAI using command "symAI.py --plan v0.json"


symAI adds this plan to the set of global constraints and verifies satisfiability. Here is the result (also available in file v0.UNSAT_core):

```
At t=1, UNSAT Core contains 1 constraints:
  BotB_move_1
At t=1, UNSAT Core contains 1 constraints:
  BotB_1_self_avoid_0_1
```

So what does it mean, in plain English? The plan failed!

- In v0, Deepseek proposed a plan
- At t=1, Robot "BotB" encountered a robotics law motion violation
- At t=1, Robot "BobB" also bumped into its own tether

### The revised plan (V1)
When notified of this result, Deepseek gains a quick understanding of the problem and fixes the issue in a V1

This time, running the new code v1.deepseek_planner.py locally and submitting the JSON plan, v1.json, to symAI returns a SAT verdict after 29 seconds of computation (on an entry-level linux VM).

The satisfiable result can be found in v1.SAT_core

## Part III: Real-time expansion
Note: the source code of the real-time expansion is available in the realtime subdirectory


We modify the set-up to support an unexpected obstacle showing up at location (6,14). We choose this location on purpose, so that it prevents bot H from executing its plan. 


To update the symbolic AI, we pass the obstacle coordinates as a command line argument: symAI.py --plan v1.json --obstacles '[(6,14)]'


As expected, plan v1 which worked well in part I, becomes unsatisfiable. SymAI returns an UNSAT core

t takes 5 iterations for Deepseek to find a satisfiable workaround. Deepseek's final plan, v7. It takes about 38 seconds for symAI to validate it on my standard VM. (So take the word "realtime" with a pinch of salt, here!).

## Conclusion

LLMs are actually great at solving problems the way humans do, with intuition and creative thinking. But here's the catch: their hallucinations make them too unreliable for anything mission-critical.

We built a hybrid system that keeps the best part (the creative problem-solving) while fixing the reliability issue. We added a symbolic AI layer that acts like a fact-checker, catching and correcting hallucinations before they cause problems.

The real game-changer is using a Digital Twin as a "smart bouncer" between the AI and the real world. Nothing gets through without passing the symbolic AI validation first, so no hallucinations are allowed by design.

But here's where it gets really cool: we made the whole system time-aware. Instead of just solving static problems, our Digital Twin can handle real-time changes and unexpected events as they happen. This is huge for real-world applications.



### License
LICENSE: CC-BY-4.0, labyrinthinesecurity
