# Practice 06 — ROS 2 Action Server & Client

## Objective

Implement a ROS 2 Action Server and Client in Python to understand goal handling, feedback, results, and cancellation through the Fibonacci action.

## Development Environment

- Ubuntu 24.04 LTS
- ROS 2 Jazzy Jalisco
- Python 3.12
- `rclpy`, `action_tutorials_interfaces`, `action_msgs`

## Project Structure

```text
06_action/
├── action_server.py
├── action_client.py
├── README.md
└── CODE_WALKTHROUGH.md
```

## Communication Overview

**Action:** `/fibonacci`  
**Interface:** `action_tutorials_interfaces/action/Fibonacci`

| Direction | Field | Description |
|---|---|---|
| Client → Server (Goal) | `order` (`int32`) | Requested number of Fibonacci terms |
| Server → Client (Feedback) | `partial_sequence` (`int32[]`) | Sequence generated so far |
| Server → Client (Result) | `sequence` (`int32[]`) | Final or partial sequence |

The client sends a goal asynchronously, receives feedback while the server executes, then receives the result and final goal status. It can also request cancellation.

## Implementation Summary

- **`action_server.py`:** Creates an `ActionServer`, generates Fibonacci numbers, publishes feedback, accepts cancel requests, and sets the goal's terminal status. Uses a `ReentrantCallbackGroup` and `MultiThreadedExecutor` to allow cancel callbacks during goal execution.
- **`action_client.py`:** Sends an asynchronous goal, checks whether it was accepted, handles feedback, requests cancellation when configured, and reports the result and status.
- **Cancellation test:** Change `self.cancel_after = 0` to `self.cancel_after = 3` in `action_client.py` to request cancellation after three feedback messages. Restore it to `0` afterward.

## How to Run

Ensure ROS 2 Jazzy and the action interface package are available:

```bash
source /opt/ros/jazzy/setup.bash
ros2 interface show action_tutorials_interfaces/action/Fibonacci
```

If the interface is missing:

```bash
sudo apt update
sudo apt install ros-jazzy-action-tutorials-interfaces
```

**Terminal 1 — Action Server**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/06_action
python3 action_server.py
```

**Terminal 2 — Action Client**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/06_action
python3 action_client.py
```

With `order=10`, the expected result is `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`. After the result is displayed, the client keeps spinning; press `Ctrl+C` to exit. Stop the server with `Ctrl+C` as well.

## Useful ROS 2 Commands

```bash
ros2 action list -t
ros2 action info /fibonacci
ros2 interface show action_tutorials_interfaces/action/Fibonacci
ros2 action send_goal --feedback /fibonacci action_tutorials_interfaces/action/Fibonacci "{order: 7}"
```

## What I Learned

- How Actions differ from one-way Topic streaming and request-response Services.
- How Goal, Feedback, and Result relate during long-running tasks.
- How asynchronous Futures and callbacks handle action responses.
- How to request cancellation and observe a canceled goal status.

## Conclusion

This practice demonstrates asynchronous goal execution, progress feedback, final results, and cancellation using ROS 2 Actions. The same communication pattern can later support robot navigation and arm motions.
