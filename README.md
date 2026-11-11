# ROS2 Practice

A collection of hands-on ROS2 exercises using **Python**, developed to understand ROS2 communication, node control, and robot application development step by step.

The repository focuses on implementing, running, and verifying ROS2 programs rather than studying concepts alone. Each practice is organized independently and will be expanded as new topics are covered.

## Development Environment

| Component | Version / Tool |
| --- | --- |
| Operating System | Ubuntu 24.04 LTS |
| ROS2 Distribution | Jazzy Jalisco |
| Programming Language | Python 3.12 |
| ROS2 Python Library | `rclpy` |
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

More practices will be added as the project progresses.

## Project Structure

```text
ros2_practice/
├── README.md
├── 01_publisher_subscriber/
│   ├── publisher.py
│   ├── subscriber.py
│   ├── README.md
│   └── CODE_WALKTHROUGH.md
├── 02_turtlesim_control/
│   ├── turtle_controller.py
│   ├── turtle_pose.py
│   ├── README.md
│   └── CODE_WALKTHROUGH.md
├── 03_service_client/
│   ├── service_server.py
│   ├── service_client.py
│   ├── turtle_teleport.py
│   ├── README.md
│   └── CODE_WALKTHROUGH.md
├── 04_ros2_parameters/
│   └── parameter_turtle_controller.py
└── 05_launch_file/
    └── launch/
        └── turtlesim_mimic.launch.py
```

Each practice may include two documentation files:

- **`README.md`** — A concise English guide covering the objective, implementation, and execution steps.
- **`CODE_WALKTHROUGH.md`** — A detailed Korean explanation of the actual Python source code, including syntax, ROS2 APIs, callbacks, and execution flow.

## Practice Highlights

### 01 — Publisher & Subscriber

Implemented Python nodes that exchange messages through a ROS2 topic. Learned how publishers, subscribers, message types, and callback functions work together.

### 02 — Turtlesim Control

Used Python nodes to command a simulated turtle and observe its pose. Practiced velocity commands and feedback through ROS2 topics.

### 03 — Service & Client

Implemented a service server and client for request-response communication. Also explored Turtlesim's teleportation service to control a turtle through a service call.

### 04 — ROS2 Parameters

Implemented a Turtlesim controller with configurable linear and angular speeds. Practiced changing parameters at runtime and validating parameter values.

### 05 — ROS2 Launch Files

Created a Python launch file to start two namespaced Turtlesim nodes and a mimic node together. Practiced namespaces, topic remapping, and node parameters in a multi-node application.

## Getting Started

### 1. Set up the ROS2 environment

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
```

The domain ID above is the value used for these exercises. Communicating ROS2 processes must use compatible domain settings.

### 2. Clone the repository

```bash
git clone https://github.com/kwwmm/ros2-practice.git
cd ros2-practice
```

### 3. Run a practice

Follow the instructions in the `README.md` inside each practice directory. Most standalone Python nodes can be started with `python3`, while the launch-file practice uses `ros2 launch`.

Example:

```bash
cd 01_publisher_subscriber
python3 publisher.py
```

Run the corresponding subscriber in another terminal with the same ROS2 environment configured.

## Useful ROS2 Commands

```bash
ros2 node list
ros2 topic list
ros2 topic echo /topic_name
ros2 topic info /topic_name
ros2 service list
ros2 service type /service_name
ros2 param list
ros2 param get /node_name parameter_name
```

## Long-Term Goal

The long-term goal is to apply these ROS2 fundamentals to a robotics capstone project integrating:

- A ROS2-based mobile robot
- Camera-based object detection
- Robotic arm control
- Reinforcement learning for motion and control optimization

Future practices will gradually connect ROS2 communication and control concepts to real robotic systems.

## Progress

**Current scope:** Practices 01–05 (Publisher/Subscriber → Turtlesim → Service/Client → Parameters → Launch Files).

This is an ongoing learning repository. New implementations and documentation will be added as each practice progresses.