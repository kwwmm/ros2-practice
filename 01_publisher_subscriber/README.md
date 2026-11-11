# 01. ROS2 Publisher & Subscriber

## 1. Objective

This practice focuses on understanding the basic communication structure of ROS2 by implementing Publisher and Subscriber nodes using Python.

The main objectives are:

- Understand ROS2 Nodes and Topics.
- Implement Publisher and Subscriber nodes using `rclpy`.
- Exchange string messages through a Topic.
- Understand timer-based publishing and callback functions.
- Monitor node communication using ROS2 CLI tools.

## 2. Development Environment

- **OS:** Ubuntu 24.04 LTS
- **ROS2 Distribution:** Jazzy Jalisco
- **Language:** Python 3.12
- **Libraries:** `rclpy`, `std_msgs`

## 3. Project Structure

```text
01_publisher_subscriber/
├── publisher.py
├── subscriber.py
└── README.md
```

| File | Description |
|---|---|
| `publisher.py` | Publishes string messages every second |
| `subscriber.py` | Receives and displays messages |
| `README.md` | Documentation for this practice |

## 4. ROS2 Communication Overview

ROS2 uses a publish-subscribe communication model, allowing independent nodes to exchange messages through Topics.

| Component | Description |
|---|---|
| Node | An independent component that performs a specific task |
| Publisher | Sends messages to a Topic |
| Subscriber | Receives messages from a Topic |
| Topic | A named communication channel |

### Communication Structure

```text
  my_publisher
       |
       | std_msgs/msg/String
       v
   /my_topic
       |
       v
  my_subscriber
```

- **Publisher Node:** `/my_publisher`
- **Subscriber Node:** `/my_subscriber`
- **Topic:** `/my_topic`
- **Message Type:** `std_msgs/msg/String`
- **Publishing Frequency:** Approximately 1 Hz

Both nodes use the same Topic name and compatible message types to communicate.

## 5. Publisher & Subscriber

### Publisher

The Publisher sends a string message every second using a timer.

- `create_publisher()`: Creates a Publisher for the specified Topic.
- `create_timer()`: Executes a callback periodically.
- `publish()`: Sends a message to the Topic.

### Subscriber

The Subscriber receives messages from `/my_topic` and displays them in the terminal.

- `create_subscription()`: Subscribes to the specified Topic.
- `listener_callback()`: Processes incoming messages.
- `rclpy.spin()`: Keeps the node running and processes callbacks.

## 6. How to Run

### Terminal 1 — Publisher

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/01_publisher_subscriber
python3 publisher.py
```

### Terminal 2 — Subscriber

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/01_publisher_subscriber
python3 subscriber.py
```

### Expected Output

**Publisher:**

```text
Publishing: Hello ROS2! Count: 0
Publishing: Hello ROS2! Count: 1
Publishing: Hello ROS2! Count: 2
```

**Subscriber:**

```text
Received: Hello ROS2! Count: 0
Received: Hello ROS2! Count: 1
Received: Hello ROS2! Count: 2
```

The received counter values depend on when the Subscriber starts.

## 7. Useful ROS2 Commands

```bash
ros2 node list
ros2 topic list
ros2 topic echo /my_topic
ros2 topic hz /my_topic
ros2 topic info /my_topic -v
rqt_graph
```

These commands can be used to inspect active nodes, monitor messages, measure publishing frequency, and visualize communication.

## 8. What I Learned

Through this practice, I learned:

1. How to implement Publisher and Subscriber nodes using Python.
2. How ROS2 Nodes communicate through Topics.
3. How to use `std_msgs/msg/String` messages.
4. How timers and callbacks work in ROS2.
5. How to inspect and visualize ROS2 communication.

## 9. Conclusion

This practice demonstrated the fundamentals of ROS2 communication using Publisher and Subscriber nodes.

It provides a foundation for future practices involving robot motion control, sensor data processing, and autonomous robotics.