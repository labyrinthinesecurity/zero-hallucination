import json

def generate_robot_plan():
    grid_size = 30
    num_robots = 10
    T = 30  # Increased timesteps to allow for more complex paths
    
    robot_names = ['BotA', 'BotB', 'BotC', 'BotD', 'BotE', 'BotF', 'BotG', 'BotH', 'BotI', 'BotJ']
    
    starts = [(0, 2*i) for i in range(num_robots)]
    goals = [(10, 2*i+1) for i in range(num_robots)]
    
    paths = {name: [] for name in robot_names}
    
    for i, name in enumerate(robot_names):
        start_x, start_y = starts[i]
        goal_x, goal_y = goals[i]
        current_x, current_y = start_x, start_y
        
        path = []
        
        # Calculate optimal path with detours to avoid collisions
        horizontal_steps = (goal_x - start_x) % grid_size
        vertical_steps = (goal_y - start_y) % grid_size
        
        # For even-indexed robots, move up first then right
        # For odd-indexed robots, move right first then up
        # This creates alternating paths to avoid collisions
        
        for t in range(T):
            if current_x == goal_x and current_y == goal_y:
                # At goal, stay there
                path.append((current_x, current_y))
                continue
                
            # Different movement patterns based on robot index
            if i % 2 == 0:  # Even-indexed robots (A, C, E, G, I)
                if current_y != goal_y:
                    # Move vertically toward goal
                    if (goal_y - current_y) % grid_size <= grid_size // 2:
                        current_y = (current_y + 1) % grid_size
                    else:
                        current_y = (current_y - 1) % grid_size
                else:
                    # Move horizontally toward goal
                    if (goal_x - current_x) % grid_size <= grid_size // 2:
                        current_x = (current_x + 1) % grid_size
                    else:
                        current_x = (current_x - 1) % grid_size
            else:  # Odd-indexed robots (B, D, F, H, J)
                if current_x != goal_x:
                    # Move horizontally toward goal
                    if (goal_x - current_x) % grid_size <= grid_size // 2:
                        current_x = (current_x + 1) % grid_size
                    else:
                        current_x = (current_x - 1) % grid_size
                else:
                    # Move vertically toward goal
                    if (goal_y - current_y) % grid_size <= grid_size // 2:
                        current_y = (current_y + 1) % grid_size
                    else:
                        current_y = (current_y - 1) % grid_size
            
            path.append((current_x, current_y))
        
        paths[name] = path
    
    return paths

def main():
    plan = generate_robot_plan()
    json_output = json.dumps(plan, indent=2)
    print(json_output)

if __name__ == "__main__":
    main()
