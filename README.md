# 02. ROS2 Turtlesim Control

## 1. Objective

This practice focuses on controlling a simulated robot using ROS2 Jazzy and Python, applying the Publisher and Subscriber concepts learned in the previous practice.

The main objectives are:

- Understand how to launch and operate the Turtlesim simulator.
- Control a simulated turtle using keyboard commands.
- Implement a custom Python Publisher for robot motion control.
- Understand linear and angular velocities using `geometry_msgs/msg/Twist`.
- Generate circular trajectories by combining linear and angular velocity.
- Implement a custom Subscriber to monitor the turtle's position and orientation.
- Analyze ROS2 communication using command-line tools and `rqt_graph`.

## 2. Development Environment

- **OS:** Ubuntu 24.04 LTS
- **ROS2 Distribution:** Jazzy Jalisco
- **Language:** Python 3.12
- **Libraries:** `rclpy`, `geometry_msgs`, `turtlesim`
- **Simulator:** Turtlesim

### Required Package

If Turtlesim is not installed, install it using:

```bash
sudo apt update
sudo apt install ros-jazzy-turtlesim
```

## 3. Project Structure

```text
02_turtlesim_control/
├── turtle_controller.py
├── turtle_pose.py
└── README.md
```

| File | Description |
|---|---|
| `turtle_controller.py` | Publishes velocity commands to move the turtle automatically |
| `turtle_pose.py` | Subscribes to and displays the turtle's position and orientation |
| `README.md` | Documentation for this practice |

## 4. ROS2 Turtlesim Overview

Turtlesim is a lightweight 2D robot simulator provided for learning fundamental ROS2 concepts.

It allows users to control a virtual turtle and observe its position, orientation, and movement trajectory.

### 4.1 Main Components

This practice uses three ROS2 nodes:

| Node | Role |
|---|---|
| `/turtlesim` | Simulates the turtle's movement and publishes its current state |
| `/turtle_controller` | Publishes velocity commands to control the turtle |
| `/turtle_pose_reader` | Subscribes to the turtle's position and orientation |

The default keyboard teleoperation node is also used during manual control.

### 4.2 ROS2 Topics

Two main topics are used:

| Topic | Message Type | Purpose |
|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Sends linear and angular velocity commands |
| `/turtle1/pose` | `turtlesim/msg/Pose` | Provides the current position and orientation |

The controller publishes commands to `/turtle1/cmd_vel`, while the simulator publishes the turtle's pose to `/turtle1/pose`.

## 5. Keyboard Control

Before implementing a custom controller, the turtle can be controlled using the keyboard teleoperation node provided by Turtlesim.

### 5.1 Start Turtlesim

**Terminal 1**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13

ros2 run turtlesim turtlesim_node
```

A simulator window appears with a turtle at approximately the center of the screen.

### 5.2 Start Keyboard Teleoperation

**Terminal 2**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13

ros2 run turtlesim turtle_teleop_key
```

The terminal must have keyboard focus for the controls to work.

### 5.3 Keyboard Commands

| Key | Action |
|---|---|
| ↑ | Move forward |
| ↓ | Move backward |
| ← | Rotate counterclockwise |
| → | Rotate clockwise |

### 5.4 Communication Principle

The keyboard teleoperation program is an existing ROS2 executable.

It converts keyboard inputs into velocity commands and publishes them to `/turtle1/cmd_vel`.

```text
Keyboard Input
      |
      v
turtle_teleop_key
      |
      | geometry_msgs/msg/Twist
      v
/turtle1/cmd_vel
      |
      v
   turtlesim
      |
      v
 Turtle Movement
```

The turtle moves according to the received velocity commands.

Unlike the keyboard teleoperation node, the automatic controller in the next section is implemented directly in Python.

## 6. Automatic Turtle Control Using Python

A custom Publisher node was implemented to control the turtle automatically.

The controller continuously publishes linear and angular velocity commands to produce circular motion.

### 6.1 Run the Controller

Keep the Turtlesim simulator running.

Stop keyboard teleoperation using `Ctrl+C` before starting the custom controller.

**Terminal 2**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13

cd ~/ros2_practice/02_turtlesim_control
python3 turtle_controller.py
```

### 6.2 Core Implementation

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')

        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.move_turtle
        )

    def move_turtle(self):
        msg = Twist()

        msg.linear.x = 2.0
        msg.angular.z = 1.0

        self.publisher.publish(msg)
```

### 6.3 Code Explanation

**Creating the Node**

```python
super().__init__('turtle_controller')
```

Initializes the ROS2 node with the name `turtle_controller`.

**Creating the Publisher**

```python
self.publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

| Parameter | Description |
|---|---|
| `Twist` | Velocity message type |
| `/turtle1/cmd_vel` | Topic used to send motion commands |
| `10` | QoS history depth using the default QoS profile |

**Creating the Timer**

```python
self.timer = self.create_timer(
    0.1,
    self.move_turtle
)
```

This timer calls `move_turtle()` approximately every 0.1 seconds.

The theoretical publishing frequency is calculated as:

$$
f = \frac{1}{T}
$$

where:

- $f$: Publishing frequency in Hz
- $T