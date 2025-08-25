#!/usr/bin/python3

import json

def generate_robot_plan():
    grid_size = 30
    num_robots = 10
    T = 35

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

        for t in range(1, T):
            if current_x == goal_x and current_y == goal_y:
                path.append((current_x, current_y))
                continue

            next_x, next_y = current_x, current_y

            # Special handling for BotH to avoid obstacle at (6,14)
            if name == 'BotH':
                # BotH: Go right to x=4, then down to y=13, then right to x=10, then up to y=15
                if current_x < 4:
                    next_x = (current_x + 1) % grid_size
                elif current_x == 4 and current_y == 14:
                    next_y = (current_y - 1) % grid_size  # Move down to y=13
                elif current_x == 4 and current_y == 13:
                    next_x = (current_x + 1) % grid_size  # Move right to x=5
                elif current_x >= 5 and current_x < goal_x:
                    next_x = (current_x + 1) % grid_size
                elif current_x == goal_x and current_y < goal_y:
                    next_y = (current_y + 1) % grid_size
                else:
                    # Default movement
                    if current_x < goal_x:
                        next_x = (current_x + 1) % grid_size
                    else:
                        next_y = (current_y + 1) % grid_size

            # Special handling for BotG to avoid collision with BotH
            elif name == 'BotG':
                # BotG: Go right to x=5, then wait one step, then continue
                if current_x < 5:
                    next_x = (current_x + 1) % grid_size
                elif current_x == 5 and current_y == 12 and t < 7:
                    # Wait at (5,12) for one timestep to let BotH pass through (5,13)
                    next_x, next_y = current_x, current_y
                elif current_x == 5 and current_y == 12:
                    next_y = (current_y + 1) % grid_size  # Move up to y=13
                elif current_x == 5 and current_y == 13:
                    next_x = (current_x + 1) % grid_size  # Move right to x=6
                elif current_x < goal_x:
                    next_x = (current_x + 1) % grid_size
                elif current_y < goal_y:
                    next_y = (current_y + 1) % grid_size
                else:
                    next_y = (current_y - 1) % grid_size

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

            current_x, current_y = next_x, next_y
            path.append((current_x, current_y))

        paths[name] = path

    return paths

def main():
    plan = generate_robot_plan()
    json_output = json.dumps(plan, indent=2)
    print(json_output)

if __name__ == "__main__":
    main()
