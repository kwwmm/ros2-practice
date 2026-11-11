# 02. ROS2 Turtlesim Control

## 1. Objective

This practice focuses on controlling a simulated robot using ROS2 Jazzy and Python.

The main objectives are:

- Run the Turtlesim simulator.
- Control the turtle manually using keyboard inputs.
- Implement a Python Publisher to control the turtle automatically.
- Understand linear and angular velocity using `Twist` messages.
- Implement a Subscriber to monitor the turtle's position and orientation.
- Understand communication between ROS2 nodes using Topics.

## 2. Development Environment

- **OS:** Ubuntu 24.04 LTS
- **ROS2 Distribution:** Jazzy Jalisco
- **Language:** Python 3.12
- **Libraries:** `rclpy`, `geometry_msgs`, `turtlesim`

## 3. Project Structure

```text
02_turtlesim_control/
├── turtle_controller.py
├── turtle_pose.py
└── README.md
```

| File | Description |
|---|---|
| `turtle_controller.py` | Publishes velocity commands to control the turtle |
| `turtle_pose.py` | Subscribes to the turtle's position and orientation |
| `README.md` | Documentation for the practice |

## 4. Keyboard Control

The `turtle_teleop_key` node, provided by the Turtlesim package, allows the turtle to be controlled using keyboard inputs.

**Terminal 1 — Start Turtlesim**

```bash
ros2_study
ros2 run turtlesim turtlesim_node
```

**Terminal 2 — Keyboard Control**

```bash
ros2_study
ros2 run turtlesim turtle_teleop_key
```

**Keyboard Controls**

| Key | Action |
|---|---|
| ↑ | Move forward |
| ↓ | Move backward |
| ← | Rotate counterclockwise |
| → | Rotate clockwise |

The keyboard control node publishes velocity commands to the `/turtle1/cmd_vel` topic using `geometry_msgs/msg/Twist` messages.

## 5. Automatic Turtle Control

A custom Python Publisher node was implemented to control the turtle automatically.

### Execution

Keep the Turtlesim simulator running and execute:

```bash
ros2_study
cd ~/ros2_practice/02_turtlesim_control
python3 turtle_controller.py
```

### Core Code

```python
msg = Twist()

msg.linear.x = 2.0
msg.angular.z = 1.0

self.publisher.publish(msg)
```

### Explanation

- `linear.x`: Forward linear velocity
- `angular.z`: Angular velocity around the Z-axis
- `/turtle1/cmd_vel`: Topic used to send velocity commands
- `Twist`: ROS2 message type containing linear and angular velocity components

By applying constant linear and angular velocities simultaneously, the turtle follows a circular trajectory.

The turning radius can be calculated as:

\[
R = \frac{|v|}{|\omega|}
\]

where:

- \(v\): Linear velocity
- \(\omega\): Angular velocity

For the current configuration:

\[
R = \frac{2.0}{1.0} = 2.0
\]

The turtle follows a circular path with a theoretical radius of 2.0 simulation units, assuming no boundary interference.

## 6. Turtle Pose Subscriber

A custom Subscriber node was implemented to receive the turtle's position and orientation in real time.

### Execution

Open another terminal while the simulator is running:

```bash
ros2_study
cd ~/ros2_practice/02_turtlesim_control
python3 turtle_pose.py
```

### Core Code

```python
self.subscription = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.pose_callback,
    10
)
```

### Received Data

| Field | Description |
|---|---|
| `x` | Position along the X-axis |
| `y` | Position along the Y-axis |
| `theta` | Orientation angle in radians |

The Subscriber receives messages of type `turtlesim/msg/Pose` from the `/turtle1/pose` topic.

## 7. ROS2 Communication Structure