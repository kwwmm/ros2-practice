# Practice 04 — ROS2 Parameters & Dynamic Control

## Objective

Control a Turtlesim robot using ROS2 parameters. Change its linear and angular speeds at runtime without editing the Python source code or restarting the controller node, and reject invalid parameter values.

## Development Environment

- **OS:** Ubuntu 24.04 LTS
- **ROS2:** Jazzy Jalisco
- **Python:** 3.12
- **Simulator:** `turtlesim`
- **ROS_DOMAIN_ID:** `13` (this practice environment)

## Project Structure

```text
04_ros2_parameters/
├── parameter_turtle_controller.py
├── README.md
└── CODE_WALKTHROUGH.md
```

- `parameter_turtle_controller.py`: Declares speed parameters, validates updates, and publishes velocity commands.
- `README.md`: Practice overview and execution instructions.
- `CODE_WALKTHROUGH.md`: Detailed Korean analysis of the Python code.

## Communication Overview

```text
ROS2 CLI (ros2 param set)
        |
        v
/parameter_turtle_controller
  - linear_speed: 2.0 (default)
  - angular_speed: 1.0 (default)
  - on-set validation callback
  - 0.1 s timer callback
        |
        | /turtle1/cmd_vel (geometry_msgs/msg/Twist)
        v
     /turtlesim
```

| Item | Description |
|---|---|
| Controller node | `/parameter_turtle_controller` |
| Simulator node | `/turtlesim` |
| Topic | `/turtle1/cmd_vel` |
| Message type | `geometry_msgs/msg/Twist` |
| Publish period | `0.1 s` (approximately `10 Hz`) |
| `linear_speed` | Double, default `2.0`, valid range `0.0 < value <= 5.0` |
| `angular_speed` | Double, default `1.0`, valid range `0.0 < value <= 5.0` |

## Implementation Summary

- Declare two ROS2 parameters with `declare_parameter()`.
- Create a `Twist` publisher for Turtlesim velocity commands.
- Register an on-set callback that rejects non-double values and speeds outside the allowed range.
- Read the current parameter values in a timer callback and publish a velocity command every `0.1 s`.
- Process callbacks using `rclpy.spin()` and clean up when interrupted.

## How to Run

Open three terminals and run the commands below.

**Terminal 1 — Turtlesim**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
ros2 run turtlesim turtlesim_node
```

**Terminal 2 — Controller**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/04_ros2_parameters
python3 parameter_turtle_controller.py
```

**Terminal 3 — ROS2 CLI**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13

ros2 param get /parameter_turtle_controller linear_speed
ros2 param get /parameter_turtle_controller angular_speed

ros2 param set /parameter_turtle_controller linear_speed 1.0
ros2 param set /parameter_turtle_controller angular_speed 3.0
```

Stop the controller and the simulator with `Ctrl+C` in their respective terminals.

## Useful ROS2 Commands

```bash
# Inspect nodes, parameters, and the velocity topic
ros2 node list
ros2 param list /parameter_turtle_controller
ros2 topic info /turtle1/cmd_vel
ros2 topic hz /turtle1/cmd_vel
ros2 topic echo /turtle1/cmd_vel --once

# Test parameter validation (expected to be rejected)
ros2 param set /parameter_turtle_controller linear_speed 0.0
ros2 param get /parameter_turtle_controller linear_speed
```

## Verification Results

The following results were observed during this practice:

- Both `/parameter_turtle_controller` and `/turtlesim` appeared in `ros2 node list`.
- The velocity topic reported **1 publisher** and **1 subscriber**.
- The measured publish rate was approximately **10 Hz** (`9.996–10.000 Hz` in the captured output).
- Both runtime parameter updates (`1.0` and `3.0`) returned `Set parameter successful`.
- A subsequent `Twist` message contained `linear.x = 1.0` and `angular.z = 3.0`.
- Setting `linear_speed` to `0.0` was rejected; the parameter remained `1.0`.

## What I Learned

- How to declare and read typed ROS2 parameters.
- How to modify node behavior through ROS2 CLI without restarting it.
- How an on-set parameter callback validates proposed changes.
- How a timer callback uses updated parameters when publishing `Twist` messages.
- How to inspect ROS2 nodes, topic connections, and message frequencies.

## Conclusion

This practice demonstrates runtime configuration of a ROS2 velocity controller. The same parameter-management pattern can be extended to mobile robot speed limits and controller gains.
