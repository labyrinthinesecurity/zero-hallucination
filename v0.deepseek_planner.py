import json

def generate_robot_plan():
    grid_size = 30
    num_robots = 10
    T = 25  # Total timesteps
    
    # Robot names
    robot_names = ['BotA', 'BotB', 'BotC', 'BotD', 'BotE', 'BotF', 'BotG', 'BotH', 'BotI', 'BotJ']
    
    # Start and goal positions
    starts = [(0, 2*i) for i in range(num_robots)]
    goals = [(10, 2*i+1) for i in range(num_robots)]
    
    # Initialize paths
    paths = {name: [] for name in robot_names}
    
    # Generate movement plan for each robot
    for i, name in enumerate(robot_names):
        start_x, start_y = starts[i]
        goal_x, goal_y = goals[i]
        current_x, current_y = start_x, start_y
        
        path = []
        
        # Move horizontally first (to x=10)
        horizontal_steps = (goal_x - start_x) % grid_size
        if horizontal_steps > grid_size // 2:
            horizontal_steps = horizontal_steps - grid_size
        
        # Move vertically to target y
        vertical_steps = (goal_y - start_y) % grid_size
        if vertical_steps > grid_size // 2:
            vertical_steps = vertical_steps - grid_size
        
        # Add delay based on robot index to avoid collisions
        delay = i * 2
        
        for t in range(T):
            if t < delay:
                # Wait at start position
                path.append((current_x, current_y))
                continue
                
            if current_x == goal_x and current_y == goal_y:
                # Already at goal, stay there
                path.append((current_x, current_y))
                continue
                
            # Move horizontally if not at target x
            if current_x != goal_x:
                if horizontal_steps > 0:
                    current_x = (current_x + 1) % grid_size
                else:
                    current_x = (current_x - 1) % grid_size
                    if current_x < 0:
                        current_x += grid_size
            # Move vertically if at target x but not target y
            elif current_y != goal_y:
                if vertical_steps > 0:
                    current_y = (current_y + 1) % grid_size
                else:
                    current_y = (current_y - 1) % grid_size
                    if current_y < 0:
                        current_y += grid_size
            
            path.append((current_x, current_y))
        
        paths[name] = path
    
    return paths

def main():
    plan = generate_robot_plan()
    
    # Convert to JSON format
    json_output = json.dumps(plan, indent=2)
    print(json_output)

if __name__ == "__main__":
    main()
