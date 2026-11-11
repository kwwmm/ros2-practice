# Practice 05 — ROS 2 Launch File

## Objective

Launch two Turtlesim nodes and one Mimic node from a single Python launch file. Practice ROS 2 namespaces, topic remapping, and node parameters.

## Development Environment

- Ubuntu 24.04 LTS
- ROS 2 Jazzy Jalisco
- Python 3.12
- `turtlesim`, `launch`, `launch_ros`

## Project Structure

```text
05_launch_file/
├── launch/
│   └── turtlesim_mimic.launch.py
├── README.md
└── CODE_WALKTHROUGH.md
```

## Communication Overview

```text
/turtlesim1/sim
   publishes /turtlesim1/turtle1/pose
                 |
                 v
              /mimic
                 |
   publishes /turtlesim2/turtle1/cmd_vel
                 |
                 v
           /turtlesim2/sim
```

| Node | Executable | Purpose |
|---|---|---|
| `/turtlesim1/sim` | `turtlesim_node` | First simulator; publishes the source pose |
| `/turtlesim2/sim` | `turtlesim_node` | Second simulator; receives movement commands |
| `/mimic` | `mimic` | Converts the source pose into commands for the second simulator |

## Implementation Summary

- `LaunchDescription` declares three ROS 2 nodes.
- `namespace` isolates the two simulators even though both nodes use the name `sim`.
- `parameters` sets distinct background colors.
- `remappings` connects the source pose to Mimic and Mimic's velocity output to the second turtle.

## How to Run

**Terminal 1 — launch the nodes**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
ros2 launch ~/ros2_practice/05_launch_file/launch/turtlesim_mimic.launch.py
```

**Terminal 2 — control the first turtle**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
ros2 run turtlesim turtle_teleop_key --ros-args -r __ns:=/turtlesim1
```

Focus Terminal 2 and use the arrow keys. The second turtle responds through the Mimic node. **Mimic is not a direct copy of the first turtle's `cmd_vel` topic**, so the turtles need not move in identical directions.

Press `Ctrl+C` in the terminals to stop the processes.

## Useful ROS 2 Commands

```bash
ros2 node list
ros2 node info /mimic
ros2 topic list
ros2 topic echo /turtlesim1/turtle1/pose
ros2 topic echo /turtlesim2/turtle1/cmd_vel
ros2 param get /turtlesim1/sim background_b
```

Expected nodes: `/turtlesim1/sim`, `/turtlesim2/sim`, `/mimic`. The first background's blue parameter is configured as `255`.

## What I Learned

- Run several ROS 2 nodes using one Python launch file.
- Use namespaces to prevent node and topic name conflicts.
- Connect existing nodes with topic remapping without editing their source code.
- Supply node parameters when launching a system.

## Conclusion

This practice demonstrates how ROS 2 Launch composes multiple processes into a single system. The same approach can later be used to start camera, perception, and robot-control nodes together.
