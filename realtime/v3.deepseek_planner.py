#!/usr/bin/python3

import json

def generate_robot_plan():
    grid_size = 30
    num_robots = 10
    T = 35  # More timesteps for proper detours

    robot_names = ['BotA', 'BotB', 'BotC', 'BotD', 'BotE', 'BotF', 'BotG', 'BotH', 'BotI', 'BotJ']

    starts = [(0, 2*i) for i in range(num_robots)]
    goals = [(10, 2*i+1) for i in range(num_robots)]

    paths = {name: [] for name in robot_names}
    obstacle = (6, 14)  # The unpassable tile

    for i, name in enumerate(robot_names):
        start_x, start_y = starts[i]
        goal_x, goal_y = goals[i]
        current_x, current_y = start_x, start_y

        path = [(current_x, current_y)]  # Start position at t=0

        for t in range(1, T):  # Start from t=1
            if current_x == goal_x and current_y == goal_y:
                path.append((current_x, current_y))
                continue

            next_x, next_y = current_x, current_y

            # Special handling for BotH to avoid the obstacle at (6,14)
            if name == 'BotH':
                # BotH's strategy: move right until x=5, then down to y=13, then right to x=6, then up to y=15
                if current_x < 5:
                    next_x = (current_x + 1) % grid_size  # Move right
                elif current_x == 5 and current_y == 14:
                    next_y = (current_y - 1) % grid_size  # Move down to avoid (6,14)
                elif current_x == 5 and current_y == 13:
                    next_x = (current_x + 1) % grid_size  # Move right to x=6
                elif current_x == 6 and current_y == 13:
                    next_y = (current_y + 1) % grid_size  # Move up to y=14 (but careful!)
                elif current_x == 6 and current_y == 14:
                    # We should never be here since (6,14) is obstacle, but just in case
                    next_y = (current_y + 1) % grid_size  # Move up to y=15
                else:
                    # Continue toward goal
                    if current_x < goal_x:
                        next_x = (current_x + 1) % grid_size
                    elif current_x > goal_x:
                        next_x = (current_x - 1) % grid_size
                    elif current_y < goal_y:
                        next_y = (current_y + 1) % grid_size
                    else:
                        next_y = (current_y - 1) % grid_size

            # For other bots, use normal movement patterns
            elif i % 2 == 0:  # Even-indexed robots
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
            else:  # Odd-indexed robots
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

            # Final safety check to avoid obstacle
            if (next_x, next_y) == obstacle:
                # Choose alternative move that doesn't hit obstacle
                if next_x != current_x:  # Was moving horizontally
                    next_x = current_x  # Cancel horizontal move
                    if current_y < goal_y:
                        next_y = (current_y + 1) % grid_size
                    else:
                        next_y = (current_y - 1) % grid_size
                else:  # Was moving vertically
                    next_y = current_y  # Cancel vertical move
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
