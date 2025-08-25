#!/usr/bin/python3
import json

def generate_robot_plan():
    grid_size = 30
    num_robots = 10
    T = 32  # Slightly more timesteps for detours

    robot_names = ['BotA', 'BotB', 'BotC', 'BotD', 'BotE', 'BotF', 'BotG', 'BotH', 'BotI', 'BotJ']

    starts = [(0, 2*i) for i in range(num_robots)]
    goals = [(10, 2*i+1) for i in range(num_robots)]

    paths = {name: [] for name in robot_names}
    obstacle = (6, 14)  # The unpassable tile

    for i, name in enumerate(robot_names):
        start_x, start_y = starts[i]
        goal_x, goal_y = goals[i]
        current_x, current_y = start_x, start_y

        path = []

        for t in range(T):
            if current_x == goal_x and current_y == goal_y:
                path.append((current_x, current_y))
                continue

            next_x, next_y = current_x, current_y

            # Special handling for bots that might encounter the obstacle
            if name == 'BotH':  # Most affected - starts at y=14, goal at y=15
                if current_x < 6 and current_y == 14:
                    # Move right first to avoid going directly through (6,14)
                    next_x = (current_x + 1) % grid_size
                elif current_x == 6 and current_y == 13:
                    # Move down to avoid (6,14) - go around it
                    next_y = (current_y - 1) % grid_size
                elif current_x == 6 and current_y == 15:
                    # Move right to continue path
                    next_x = (current_x + 1) % grid_size
                else:
                    # Normal movement toward goal
                    if current_x != goal_x:
                        next_x = (current_x + 1) % grid_size
                    else:
                        next_y = (current_y + 1) % grid_size

            elif name == 'BotG':  # Might pass near (6,14)
                if current_x == 6 and current_y == 13:
                    # Detour to avoid potential conflict near obstacle
                    next_x = (current_x + 1) % grid_size
                else:
                    # Normal movement
                    if current_x != goal_x:
                        next_x = (current_x + 1) % grid_size
                    else:
                        next_y = (current_y + 1) % grid_size

            elif name == 'BotI':  # Might be affected
                if current_x == 6 and current_y == 15:
                    # Small detour
                    next_x = (current_x + 1) % grid_size
                else:
                    # Normal movement
                    if current_x != goal_x:
                        next_x = (current_x + 1) % grid_size
                    else:
                        if current_y < goal_y:
                            next_y = (current_y + 1) % grid_size
                        else:
                            next_y = (current_y - 1) % grid_size

            else:  # All other bots - normal movement
                if i % 2 == 0:  # Even-indexed
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

            # Avoid the obstacle tile
            if (next_x, next_y) == obstacle:
                # If next step would hit obstacle, choose alternative
                if name == 'BotH':
                    if current_y == 14:
                        next_y = (current_y - 1) % grid_size  # Go down instead
                    else:
                        next_x = (current_x + 1) % grid_size  # Go right instead
                else:
                    next_x = (current_x + 1) % grid_size  # Default: go right

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
