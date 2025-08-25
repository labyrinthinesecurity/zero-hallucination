#!/usr/bin/python3

import json

def generate_robot_plan():
    grid_size = 30
    num_robots = 10
    T = 45  # Even more timesteps for safe path

    robot_names = ['BotA', 'BotB', 'BotC', 'BotD', 'BotE', 'BotF', 'BotG', 'BotH', 'BotI', 'BotJ']

    starts = [(0, 2*i) for i in range(num_robots)]
    goals = [(10, 2*i+1) for i in range(num_robots)]

    paths = {name: [] for name in robot_names}
    obstacle = (6, 14)

    for i, name in enumerate(robot_names):
        start_x, start_y = starts[i]
        goal_x, goal_y = goals[i]
        current_x, current_y = start_x, start_y

        path = [(current_x, current_y)]
        visited = set([(current_x, current_y)])  # Track visited cells

        for t in range(1, T):
            if current_x == goal_x and current_y == goal_y:
                path.append((current_x, current_y))
                continue

            next_x, next_y = current_x, current_y

            # BotH: Simple path avoiding obstacle
            if name == 'BotH':
                if current_x < 4:
                    next_x = (current_x + 1) % grid_size
                elif current_x == 4 and current_y == 14:
                    next_y = (current_y + 1) % grid_size  # Move up to y=15
                elif current_x >= 4 and current_x < goal_x:
                    next_x = (current_x + 1) % grid_size
                elif current_x == goal_x and current_y != goal_y:
                    if current_y < goal_y:
                        next_y = (current_y + 1) % grid_size
                    else:
                        next_y = (current_y - 1) % grid_size
                else:
                    if current_x < goal_x:
                        next_x = (current_x + 1) % grid_size
                    else:
                        next_y = (current_y + 1) % grid_size

            # BotG: Completely new path - go around the right side
            elif name == 'BotG':
                # Phase 1: Move right to x=10
                if current_x < 10:
                    next_x = (current_x + 1) % grid_size
                # Phase 2: Move up/down to target y=13
                elif current_y < 13:
                    next_y = (current_y + 1) % grid_size
                elif current_y > 13:
                    next_y = (current_y - 1) % grid_size
                else:
                    # Should be at goal (10,13)
                    next_x, next_y = current_x, current_y

            # Normal movement for other bots
            elif i % 2 == 0:  # Even-indexed
                if current_y != goal_y:
                    if (goal_y - current_y) % grid_size <= grid_size // 2:
                        next_y = (current_y + 1) % grid_size
                    else:
                        next_y = (current_y - 1) % grid_size
                else:
                    if (goal_x - current_x) % grid_size <= grid_size // 2:
                        next_x = (current_x + 1) % grid_size
                    else:
                        next_x = (current_x - 1) % grid_size
            else:  # Odd-indexed
                if current_x != goal_x:
                    if (goal_x - current_x) % grid_size <= grid_size // 2:
                        next_x = (current_x + 1) % grid_size
                    else:
                        next_x = (current_x - 1) % grid_size
                else:
                    if (goal_y - current_y) % grid_size <= grid_size // 2:
                        next_y = (current_y + 1) % grid_size
                    else:
                        next_y = (current_y - 1) % grid_size

            # Avoid obstacle
            if (next_x, next_y) == obstacle:
                if next_x != current_x:
                    next_x = current_x
                    if current_y < goal_y:
                        next_y = (current_y + 1) % grid_size
                    else:
                        next_y = (current_y - 1) % grid_size
                else:
                    next_y = current_y
                    if current_x < goal_x:
                        next_x = (current_x + 1) % grid_size
                    else:
                        next_x = (current_x - 1) % grid_size

            # Ensure we don't revisit cells
            if (next_x, next_y) in visited and (next_x, next_y) != (goal_x, goal_y):
                # If we'd revisit a cell, choose alternative move
                alternatives = []
                # Try moving in different directions
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    alt_x = (current_x + dx) % grid_size
                    alt_y = (current_y + dy) % grid_size
                    if (alt_x, alt_y) not in visited and (alt_x, alt_y) != obstacle:
                        alternatives.append((alt_x, alt_y))

                if alternatives:
                    # Choose the alternative that gets us closer to goal
                    best_alt = min(alternatives, key=lambda pos:
                                  abs(pos[0] - goal_x) + abs(pos[1] - goal_y))
                    next_x, next_y = best_alt
                else:
                    # No good alternatives, just move away from current position
                    next_x = (current_x + 1) % grid_size

            current_x, current_y = next_x, next_y
            visited.add((current_x, current_y))
            path.append((current_x, current_y))

        paths[name] = path

    return paths

def main():
    plan = generate_robot_plan()
    json_output = json.dumps(plan, indent=2)
    print(json_output)

if __name__ == "__main__":
    main()
