#!/usr/bin/python3
from z3 import *
import sys,json
import argparse
from datetime import datetime
import functools,ast
print = functools.partial(print, flush=True)    # forces flush=True for all print() calls

obstacles=''
parser = argparse.ArgumentParser()
parser.add_argument('--plan', type=str, help='a JSON file containing LLM plan')
parser.add_argument('--obstacles', type=str, help='a list of obstacle tuples')
args = parser.parse_args()

if args.obstacles is not None:
  obstacles = ast.literal_eval(args.obstacles)
  print("obstacles:")
  for o in obstacles:
    print(o)

if args.plan is None:
  print("error. You must submit a plan file")
  sys.exit()

N = 30
num_bots = 10
bots = []
start_positions = {}
goal_positions = {}


def dump_unsat(t,s):
  core = s.unsat_core()
  print(f"At t={t}, UNSAT Core contains {len(core)} constraints:")
  for i, constraint_bool in enumerate(core, 1):
      print(f"  {constraint_bool}")

for i in range(num_bots):
  bot_name = f"Bot{chr(65+i)}"  # A, B, C, ..., J
  bots.append(bot_name)
  start = (0, 2*i)
  goal = (num_bots,2*i+1)
  start_positions[bot_name] = start
  goal_positions[bot_name] = goal

print(start_positions)
print(goal_positions)

with open(args.plan, 'r') as f:
  llm_plan = json.load(f)

# Remove trailing duplicate positions from each bot's path
min_len = min(len(path) for path in llm_plan.values())
for bot in llm_plan:
    path = llm_plan[bot]
    count = 0
    for i in range(1, min_len):
        if path[-i] == path[-(i+1)]:
            count += 1
        else:
            break
    if count > 0:
        llm_plan[bot] = path[:-(count)]

# Find the longest plan length
max_len = max(len(path) for path in llm_plan.values())

# Pad each bot's plan with its last tuple until it reaches max_len
for bot, path in llm_plan.items():
    if len(path) < max_len:
        last_pos = path[-1]
        llm_plan[bot].extend([last_pos] * (max_len - len(path)))

for bot in llm_plan:
    plen=len(llm_plan[bot])
    print(plen)

with open(args.plan+'.plot', 'w') as g:
  json.dump(llm_plan,g,indent=2)

if len(llm_plan['BotA'])!=len(llm_plan['BotB']):
  print("ERROR, path len mismatch")
  sys.exit()

T=len(llm_plan['BotA'])-1
print("Timesteps:",T)
print()

s = Solver()
s.set(unsat_core=True)

positions = {}
for bot in bots:
    for t in range(T+1):
        positions[(bot,t)] = (Int(f"x_{bot}_{t}"), Int(f"y_{bot}_{t}"))

prefix_solver = Solver()

longest_valid_prefix = 0
allsat=True

for t in range(T+1):
  print(t,"..")
  constraint=True
  for bot, route in llm_plan.items():
    for u, (x_val, y_val) in enumerate(route):
      if u==t: 
        prefix_solver.assert_and_track(positions[(bot,t)][0] == x_val,Bool(f"{bot}_x_{t}_{x_val}"))
        prefix_solver.assert_and_track(positions[(bot,t)][1] == y_val,Bool(f"{bot}_y_{t}_{y_val}"))
        constraint=And(constraint,positions[(bot,t)][0] == x_val)
        constraint=And(constraint,positions[(bot,t)][1] == y_val)
  check=prefix_solver.check()
  if check==unsat:
    allsat=False

  constraint=True
  for (bot,u), (x,y) in positions.items():
    if u==t:
      prefix_solver.assert_and_track(And(x >= 0, x < N, y >= 0, y < N),Bool(f"{bot}_in_torus_{t}"))
      constraint=And(constraint,x >= 0, x < N, y >= 0, y < N)
  check=prefix_solver.check()
  if check==unsat:
      allsat=False

  constraint=True
  for bot, (xg,yg) in goal_positions.items():
    if t>0:
        x1, y1 = positions[(bot,t-1)]
        x2, y2 = positions[(bot,t)]
        dx = x2 - x1
        dy = y2 - y1
        constraint=And(
                       constraint,Or(
                                     And(Or(dx == 1, dx == -(N-1)), dy == 0),
                                     And(Or(dx == -1, dx == (N-1)), dy == 0),
                                     And(Or(dy == 1, dy == -(N-1)), dx == 0),
                                     And(Or(dy == -1, dy == (N-1)), dx == 0),
                                     And(x1 == xg, y1 == yg, x2 == xg, y2 == yg)))
        prefix_solver.assert_and_track(
                Or(
                And(Or(dx == 1, dx == -(N-1)), dy == 0), # right or wrap
                And(Or(dx == -1, dx == (N-1)), dy == 0), # left or wrap
                And(Or(dy == 1, dy == -(N-1)), dx == 0), # up or wrap
                And(Or(dy == -1, dy == (N-1)), dx == 0), # down or wrap
                And(x1 == xg, y1 == yg, x2 == xg, y2 == yg) # sit at goal
            ),
            Bool(f"{bot}_motion_law_ok_from_step_{t-1}_to_{t}")
        )
  check=prefix_solver.check()
  if check==unsat:
    allsat=False

  constraint=True
  for (bot,u), (x,y) in positions.items():
    if u==t:
      for ox, oy in obstacles:
        constraint=And(constraint,Or(x != ox, y != oy))
        prefix_solver.assert_and_track(Or(x != ox, y != oy), Bool(f"{bot}_avoid_obstacle_{t}_{ox}_{oy}"))
  check=prefix_solver.check()
  if check==unsat:
    allsat=False

  constraint=True
  for bot, (xg,yg) in goal_positions.items():
    for t1 in range(t+1):
        x1, y1 = positions[(bot,t1)]
        for t2 in range(t1+1, t+1):
            x2, y2 = positions[(bot,t2)]
            prefix_solver.push()
            constraint=And(constraint, Or(x1 != x2, y1 != y2,And(x1 == xg, y1 == yg, x2 == xg, y2 == yg)))
            self_avoid_ok = Or(
                x1 != x2, y1 != y2,
                And(x1 == xg, y1 == yg, x2 == xg, y2 == yg)
            )
            prefix_solver.assert_and_track(self_avoid_ok, Bool(f"{bot}_{t}_self_avoid_{t1}_{t2}"))
  check=prefix_solver.check()
  if check==unsat:
    allsat=False

  constraint=True
  for i, bot1 in enumerate(bots):
    for t1 in range(t,t+1):
        x1, y1 = positions[(bot1,t1)]
        xg1, yg1 = goal_positions[bot1]
        for bot2 in bots[i+1:]:
            for t2 in range(t+1):
              x2, y2 = positions[(bot2,t2)]
              xg2, yg2 = goal_positions[bot2]
              constraint=And(constraint,Or(
                    x1 != x2, y1 != y2,
                    And(x1 == xg1, y1 == yg1,
                        x2 == xg2, y2 == yg2,
                        t1 == t2)))
              mutual_avoid_ok = Or(
                    x1 != x2, y1 != y2,
                    And(x1 == xg1, y1 == yg1,
                        x2 == xg2, y2 == yg2,
                        t1 == t2)  # must be same timestep
              )
              prefix_solver.assert_and_track(mutual_avoid_ok, Bool(f"{bot1}_{bot2}_mutual_avoid_{t1}_{t2}"))

  check=prefix_solver.check()
  if check==unsat:
    allsat=False

  if allsat:
        longest_valid_prefix = t
  else:
        dump_unsat(t,prefix_solver)
        print("Longest valid prefix:", longest_valid_prefix)
        sys.exit()

print()
if allsat:
  print("SAT")
print("Longest valid prefix:", longest_valid_prefix)

