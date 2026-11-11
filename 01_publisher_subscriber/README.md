# 01. ROS2 Publisher & Subscriber

## Objective

Understand ROS2 node communication by implementing a Publisher and Subscriber in Python.

## Environment

- Ubuntu 24.04 LTS
- ROS2 Jazzy
- Python 3.12

## Files

| File | Description |
|---|---|
| `publisher.py` | Publishes a string message every second |
| `subscriber.py` | Subscribes to the topic and prints received messages |

## Communication Structure

```text
Publisher Node
      |
      | std_msgs/msg/String
      v
   /my_topic
      |
      v
Subscriber Node
```

## How to Run

**Terminal 1 — Publisher**

```bash
ros2_study
cd ~/ros2_practice/01_publisher_subscriber
python3 publisher.py
```

**Terminal 2 — Subscriber**

```bash
ros2_study
cd ~/ros2_practice/01_publisher_subscriber
python3 subscriber.py
```

## Useful Commands

```bash
ros2 node list
ros2 topic list
ros2 topic echo /my_topic
ros2 topic hz /my_topic
ros2 topic info /my_topic -v
rqt_graph
```

## What I Learned

- A node is an executable component of a ROS2 system.
- A Publisher sends messages to a Topic.
- A Subscriber receives messages from a Topic.
- Topic names and message types must match for communication.
- Multiple nodes can communicate asynchronously using the publish-subscribe model.