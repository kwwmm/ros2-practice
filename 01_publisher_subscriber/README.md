# 01. ROS2 Publisher & Subscriber

## 1. Objective

This practice focuses on understanding the basic communication structure of ROS2 by implementing Publisher and Subscriber nodes using Python.

The main objectives are:

- Understand the concept of ROS2 Nodes and Topics.
- Implement a Publisher node using `rclpy`.
- Implement a Subscriber node using `rclpy`.
- Exchange string messages between two nodes.
- Understand how asynchronous communication works in ROS2.
- Monitor active nodes, topics, and message publishing rates using ROS2 CLI tools.

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
| `subscriber.py` | Receives and displays messages from the Publisher |
| `README.md` | Documentation for this practice |

## 4. ROS2 Communication Concepts

### 4.1 Node

A Node is a fundamental execution component in ROS2.

Each node performs a specific task, such as collecting sensor data, processing information, or controlling a robot.

In this practice, two nodes are implemented:

- `my_publisher`: Publishes messages periodically.
- `my_subscriber`: Receives messages and displays them.

### 4.2 Topic

A Topic is a named communication channel used to exchange messages between ROS2 nodes.

In this practice, the topic name is:

```text
/my_topic
```

The topic name is defined in both Python files.

The Publisher and Subscriber must use compatible topic names, message types, and QoS settings to communicate.

### 4.3 Publisher

A Publisher sends messages to a specified Topic.

In this practice, the Publisher sends a string message every second.

Example:

```text
Hello ROS2! Count: 0
Hello ROS2! Count: 1
Hello ROS2! Count: 2
```

### 4.4 Subscriber

A Subscriber receives messages published to a Topic.

When a message arrives, the Subscriber executes a callback function to process the received data.

### 4.5 Communication Structure

```text
+-----------------------+
|    Publisher Node     |
|     my_publisher      |
|                       |
|     publisher.py      |
+-----------+-----------+
            |
            | std_msgs/msg/String
            v
       /my_topic
            |
            | Topic Communication
            v
+-----------+-----------+
|    Subscriber Node    |
|     my_subscriber     |
|                       |
|     subscriber.py     |
+-----------------------+
```

ROS2 uses a publish-subscribe communication model.

The Publisher and Subscriber communicate through the Topic without requiring a direct connection between the two application nodes.

## 5. Publisher Implementation

The Publisher node is implemented in `publisher.py`.

### 5.1 Core Code

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class PublisherNode(Node):
    def __init__(self):
        super().__init__('my_publisher')

        self.publisher_ = self.create_publisher(
            String,
            'my_topic',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.timer_callback
        )

        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS2! Count: {self.count}'

        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

        self.count += 1
```

### 5.2 Code Explanation

**Creating the Node**

```python
super().__init__('my_publisher')
```

Initializes the ROS2 node with the name `my_publisher`.

**Creating the Publisher**

```python
self.publisher_ = self.create_publisher(
    String,
    'my_topic',
    10
)
```

| Parameter | Description |
|---|---|
| `String` | Message type |
| `my_topic` | Topic name |
| `10` | QoS history depth using the default QoS profile |

**Creating the Timer**

```python
self.timer = self.create_timer(
    1.0,
    self.timer_callback
)
```

The timer executes `timer_callback()` approximately once every second.

The theoretical publishing frequency is:

$$
f = \frac{1}{T}
$$

where:

- $f$: Publishing frequency (Hz)
- $T$: Publishing period (seconds)

For the current configuration:

$$
f = \frac{1}{1.0} = 1.0 \text{ Hz}
$$

Therefore, the Publisher is configured to send approximately one message per second.

**Publishing the Message**

```python
msg = String()
msg.data = f'Hello ROS2! Count: {self.count}'
self.publisher_.publish(msg)
```

A `String` message is created, assigned data, and published to `/my_topic`.

The counter increases after every published message.

## 6. Subscriber Implementation

The Subscriber node is implemented in `subscriber.py`.

### 6.1 Core Code

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SubscriberNode(Node):
    def __init__(self):
        super().__init__('my_subscriber')

        self.subscription = self.create_subscription(
            String,
            'my_topic',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info(
            f'Received: {msg.data}'
        )
```

### 6.2 Code Explanation

**Creating the Subscriber**

```python
self.subscription = self.create_subscription(
    String,
    'my_topic',
    self.listener_callback,
    10
)
```

| Parameter | Description |
|---|---|
| `String` | Message type |
| `my_topic` | Topic to subscribe to |
| `self.listener_callback` | Function executed when a message arrives |
| `10` | QoS history depth using the default QoS profile |

**Receiving Messages**

```python
def listener_callback(self, msg):
    self.get_logger().info(
        f'Received: {msg.data}'
    )
```

Whenever a message arrives, the callback function reads its data and prints the received message.

### 6.3 ROS2 Execution

Both programs initialize ROS2 using:

```python
rclpy.init()
```

The following function keeps the node active and processes callbacks:

```python
rclpy.spin(node)
```

When execution ends, the node is destroyed and the ROS2 context is shut down.

## 7. How to Run

### Terminal 1 — Publisher

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_practice/01_publisher_subscriber
python3 publisher.py
```

Expected output:

```text
Publishing: Hello ROS2! Count: 0
Publishing: Hello ROS2! Count: 1
Publishing: Hello ROS2! Count: 2
```

### Terminal 2 — Subscriber

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_practice/01_publisher_subscriber
python3 subscriber.py
```

Expected output:

```text
Received: Hello ROS2! Count: 0
Received: Hello ROS2! Count: 1
Received: Hello ROS2! Count: 2
```

The actual counter value depends on when the Subscriber starts receiving messages.

Both terminals must use the same `ROS_DOMAIN_ID` to discover each other in this setup.

For example:

```bash
export ROS_DOMAIN_ID=13
```

Alternatively, the custom `ros2_study` environment command can be used on the configured development machine.

## 8. ROS2 CLI Commands

### 8.1 List Active Nodes

```bash
ros2 node list
```

Expected nodes:

```text
/my_publisher
/my_subscriber
```

### 8.2 List Available Topics

```bash
ros2 topic list
```

Relevant topics:

```text
/my_topic
/parameter_events
/rosout
```

### 8.3 Monitor Topic Messages

```bash
ros2 topic echo /my_topic
```

Example output:

```yaml
data: 'Hello ROS2! Count: 5'
---
data: 'Hello ROS2! Count: 6'
---
```

### 8.4 Check Publishing Frequency

```bash
ros2 topic hz /my_topic
```

The expected frequency is approximately:

```text
average rate: 1.0
```

### 8.5 Inspect Topic Information

```bash
ros2 topic info /my_topic -v
```

This command displays detailed information about the Topic, including its message type, publishers, subscribers, and QoS settings.

### 8.6 Inspect Node Information

```bash
ros2 node info /my_publisher
ros2 node info /my_subscriber
```

These commands show the Topics, Services, and Actions associated with each node.

### 8.7 Visualize Node Communication

```bash
rqt_graph
```

The graph visualizes the communication relationship between the Publisher, Topic, and Subscriber.

## 9. Experiment Results

The practice demonstrates the basic ROS2 publish-subscribe communication structure.

**Expected observations:**

| Test | Expected Behavior |
|---|---|
| Run Publisher | String messages are published periodically |
| Run Subscriber | Published messages are received and displayed |
| Inspect active nodes | Both custom nodes are listed |
| Inspect `/my_topic` | Publisher and Subscriber endpoints are visible |
| Monitor message frequency | Approximately 1 Hz |
| Stop Publisher | No new application messages are published |
| Restart Publisher | Message transmission resumes |

These observations can be verified using ROS2 CLI commands and the terminal output.

## 10. What I Learned

Through this practice, I learned:

1. How to create ROS2 nodes using Python and `rclpy`.
2. How to implement Publisher and Subscriber nodes.
3. How to define a custom Topic name.
4. How to exchange `std_msgs/msg/String` messages.
5. How callback functions handle incoming messages.
6. How timers control periodic message publishing.
7. How to calculate the theoretical message publishing frequency.
8. How to inspect ROS2 Nodes and Topics using CLI commands.
9. How to visualize the ROS2 communication structure using `rqt_graph`.

## 11. Conclusion

This practice introduced the fundamental communication mechanisms of ROS2 through a simple Publisher and Subscriber implementation.

By creating two independent Python nodes, I learned how ROS2 enables asynchronous message exchange using Topics.

The concepts covered in this practice provide the foundation for more advanced robotic applications, including sensor data processing, robot motion control, and autonomous navigation.

The next practice applies these concepts to the Turtlesim simulator, where velocity commands are published to control a simulated robot.