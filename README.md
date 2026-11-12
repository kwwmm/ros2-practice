# ROS2 Practice

A collection of hands-on ROS2 exercises using **Python**, developed to understand ROS2 communication, node control, and robot application development step by step.

The repository focuses on implementing, running, testing, and understanding ROS2 programs rather than studying concepts alone. Each practice is organized independently and includes practical examples that gradually build toward real robotic applications.

The exercises cover fundamental ROS2 communication mechanisms, multi-node systems, custom interfaces, and feedback-based robot control.

## Development Environment

| Component | Version / Tool |
| --- | --- |
| Operating System | Ubuntu 24.04 LTS |
| ROS2 Distribution | Jazzy Jalisco |
| Programming Language | Python 3.12 |
| ROS2 Python Library | `rclpy` |
| Build System | `colcon`, `ament_cmake` |
| Editor | Visual Studio Code |
| Terminal | Bash |

## Practice Overview

| No. | Practice | Main Concepts |
| --- | --- | --- |
| 01 | [Publisher & Subscriber](01_publisher_subscriber/) | Topics, messages, publishers, subscribers, callbacks |
| 02 | [Turtlesim Control](02_turtlesim_control/) | `Twist`, `Pose`, turtle movement and feedback |
| 03 | [Service & Client](03_service_client/) | Service servers, clients, requests, responses, Turtlesim teleportation |
| 04 | [ROS2 Parameters](04_ros2_parameters/) | Parameter declaration, runtime updates, velocity control |
| 05 | [ROS2 Launch Files](05_launch_file/) | Python launch files, namespaces, remapping, multiple nodes |
| 06 | [Action Server & Client](06_action/) | Action communication, Goal, Feedback, Result, cancellation, asynchronous callbacks |
| 07 | [Turtlesim Action Navigation](07_turtlesim_action/) | Custom Action interfaces, `colcon` builds, position feedback, P control, goal navigation |

More practices will be added as the project progresses.

## Project Structure

```text
ros2_practice/
├── README.md
├── .gitignore
│
├── 01_publisher_subscriber/
│   ├── publisher.py
│   ├── subscriber.py
│   ├── README.md
│   └── CODE_WALKTHROUGH.md
│
├── 02_turtlesim_control/
│   ├── turtle_controller.py
│   ├── turtle_pose.py
│   ├── README.md
│   └── CODE_WALKTHROUGH.md
│
├── 03_service_client/
│   ├── service_server.py
│   ├── service_client.py
│   ├── turtle_teleport.py
│   ├── README.md
│   └── CODE_WALKTHROUGH.md
│
├── 04_ros2_parameters/
│   └── parameter_turtle_controller.py
│
├── 05_launch_file/
│   └── launch/
│       └── turtlesim_mimic.launch.py
│
├── 06_action/
│   ├── action_server.py
│   ├── action_client.py
│   ├── README.md
│   └── CODE_WALKTHROUGH.md
│
└── 07_turtlesim_action/
    ├── move_server.py
    ├── move_client.py
    ├── README.md
    ├── CODE_WALKTHROUGH.md
    ├── COLCON_BUILD_GUIDE.md
    └── src/
        └── turtle_move_interfaces/
            ├── CMakeLists.txt
            ├── package.xml
            └── action/
                └── MoveToGoal.action
```

Each practice may include documentation for understanding and reproducing the implementation:

- **`README.md`** — An English guide explaining the objective, communication architecture, implementation, execution procedures, and verification methods.
- **`CODE_WALKTHROUGH.md`** — A detailed Korean explanation of the actual Python source code, including Python syntax, ROS2 APIs, callbacks, object behavior, and execution flow.
- **`COLCON_BUILD_GUIDE.md`** — An additional guide explaining the ROS2 build system, package configuration, generated interfaces, and build environment.

Generated directories such as `build/`, `install/`, and `log/` are excluded from Git tracking.

## Practice Highlights

### 01 — Publisher & Subscriber

Implemented Python nodes that exchange messages through a ROS2 topic.

Learned how publishers, subscribers, message types, and callback functions work together in asynchronous topic-based communication.

### 02 — Turtlesim Control

Used Python nodes to command a simulated turtle and observe its pose.

Practiced publishing velocity commands using `geometry_msgs/msg/Twist` and receiving position feedback using `turtlesim/msg/Pose`.

### 03 — Service & Client

Implemented a service server and client for request-response communication.

Also explored Turtlesim's teleportation service to control a turtle through a service call.

### 04 — ROS2 Parameters

Implemented a Turtlesim controller with configurable linear and angular speeds.

Practiced declaring parameters, updating values at runtime, and validating parameter changes.

### 05 — ROS2 Launch Files

Created a Python launch file to start two namespaced Turtlesim nodes and a mimic node together.

Practiced namespaces, topic remapping, node parameters, and launching multiple ROS2 nodes through a single configuration file.

### 06 — Action Server & Client

Implemented a Fibonacci Action Server and Client using Python and `rclpy`.

Explored the complete ROS2 Action communication process:

- Sending a Goal from an Action Client
- Accepting and executing the Goal on an Action Server
- Publishing intermediate Feedback during execution
- Returning the final Result
- Requesting and processing Goal cancellation

Also examined asynchronous operations, Future objects, callback functions, and multithreaded execution.

This practice introduced Action communication for long-running robotic tasks.

### 07 — Turtlesim Action Navigation

Developed an Action-based navigation system that moves a simulated turtle toward a target position.

Unlike the previous Fibonacci example, this practice integrates multiple ROS2 communication mechanisms into a working control system.

**Communication architecture:**

```text
                 Action Client
                      |
                 Target (x, y)
                      |
                      v
                 Action Server
                  /        \
                 /          \
         Pose Feedback    Velocity Command
               ^              |
               |              v
              /turtle1/pose  /turtle1/cmd_vel
                    \        /
                     Turtlesim
```

The Action Server continuously receives the turtle's current pose, calculates the distance and heading error, and publishes velocity commands.

**Key implementations:**

- Created a custom `MoveToGoal.action` interface.
- Generated ROS2 Action interfaces using `colcon build`.
- Implemented Action Server and Client nodes.
- Combined Topic communication with Action-based navigation.
- Applied proportional control to linear and angular velocity.
- Published real-time position and distance Feedback.
- Implemented Goal completion, cancellation, and invalid-target rejection.

**Verified results:**

- Successfully navigated toward the target position `(8.0, 8.0)`.
- Received real-time position and distance Feedback.
- Completed the Goal within the configured position tolerance.
- Successfully canceled an active navigation Goal and received the canceled status.

This practice demonstrates how ROS2 communication can be combined with feedback control for robotic navigation.

## Getting Started

### 1. Set Up the ROS2 Environment

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
```

The domain ID above is the value used for these exercises. Communicating ROS2 processes must use compatible domain settings.

### 2. Clone the Repository

```bash
git clone https://github.com/kwwmm/ros2-practice.git
cd ros2-practice
```

### 3. Run a Practice

Follow the instructions in the `README.md` inside each practice directory.

Most standalone Python nodes can be started directly using `python3`, while launch-file practices use `ros2 launch`.

For example, to run Practice 01:

```bash
cd 01_publisher_subscriber
python3 publisher.py
```

Run the corresponding subscriber in another terminal with the same ROS2 environment configured.

### 4. Build a Custom ROS2 Interface

Some practices, such as Practice 07, require custom ROS2 interfaces.

Before running the Python nodes, build the interface package:

```bash
cd 07_turtlesim_action

colcon build --symlink-install

source install/setup.bash
```

Verify that the custom Action interface is available:

```bash
ros2 interface show turtle_move_interfaces/action/MoveToGoal
```

After building the interface, the navigation example can be executed using separate terminals.

**Terminal 1 — Turtlesim**

```bash
ros2 run turtlesim turtlesim_node
```

**Terminal 2 — Action Server**

```bash
python3 move_server.py
```

**Terminal 3 — Action Client**

```bash
python3 move_client.py 8.0 8.0
```

Each terminal must have the appropriate ROS2 environment configured. Terminals running the custom Action nodes must also source the Practice 07 `install/setup.bash` file.

For detailed execution steps and troubleshooting, refer to the [Practice 07 README](07_turtlesim_action/README.md).

## Useful ROS2 Commands

### Nodes and Topics

```bash
ros2 node list
ros2 node info /node_name

ros2 topic list -t
ros2 topic echo /topic_name
ros2 topic info /topic_name
ros2 topic hz /topic_name
```

### Services

```bash
ros2 service list
ros2 service type /service_name
ros2 service call /service_name service_type "{request}"
```

### Parameters

```bash
ros2 param list
ros2 param get /node_name parameter_name
ros2 param set /node_name parameter_name value
```

### Actions

```bash
ros2 action list -t
ros2 action info /action_name
ros2 interface show package_name/action/ActionName
```

### Build Tools

```bash
colcon list
colcon build --symlink-install
source install/setup.bash
```

The `colcon` build process generates the files and interfaces required by ROS2 packages.

For a more detailed explanation, refer to the [COLCON Build Guide](07_turtlesim_action/COLCON_BUILD_GUIDE.md).

## Long-Term Goal

The long-term goal is to apply these ROS2 fundamentals to a robotics capstone project integrating:

- A ROS2-based mobile robot
- Camera-based object detection
- Robotic arm control
- Reinforcement learning for motion and control optimization

The practical knowledge gained from ROS2 Topics, Services, Actions, Parameters, Launch Files, and feedback control will provide a foundation for developing integrated robotic systems.

Future practices will gradually explore mobile robot control, sensor processing, camera integration, coordinate handling, robotic arm control, and reinforcement learning.

## Progress

**Current scope: Practices 01–07**

```text
01  Publisher & Subscriber
          |
02  Turtlesim Control
          |
03  Service & Client
          |
04  ROS2 Parameters
          |
05  ROS2 Launch Files
          |
06  Action Server & Client
          |
07  Turtlesim Action Navigation
```

The repository has progressed from basic node communication to custom Action interfaces and feedback-based robotic navigation.

This is an ongoing learning repository. New implementations, experiments, and documentation will be added as each practice progresses.