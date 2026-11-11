# 03. ROS2 Service & Client

## Objective

Learn how to implement request-response communication in ROS2 using Python Service Servers and Clients, and apply Service communication to control a robot in Turtlesim.

## Development Environment

- Ubuntu 24.04 LTS
- ROS2 Jazzy Jalisco
- Python 3.12
- rclpy
- Turtlesim

## Project Structure

```text
03_service_client/
├── service_server.py
├── service_client.py
├── turtle_teleport.py
└── README.md
```

## Communication Overview

Unlike Publisher/Subscriber communication, which continuously exchanges messages through Topics, Service/Client communication follows a request-response model.

- **Service Server:** Receives requests, processes them, and returns responses.
- **Service Client:** Sends requests to a Server and receives responses.
- **Request:** Contains the data required to execute an operation.
- **Response:** Contains the result of the operation.

## Implementation Summary

### 03-1. AddTwoInts Service & Client

Implemented a custom Service Server and Client using `example_interfaces/srv/AddTwoInts`.

- The Server provides the `/add_two_ints` Service.
- The Client sends two integers as a request.
- The Server calculates their sum and returns the result.
- Asynchronous Service calls are handled using `call_async()` and `spin_until_future_complete()`.

Communication:

```text
Client → Request (a, b) → Server
Client ← Response (sum) ← Server
```

### 03-2. Turtlesim Service Control

Implemented a Python Client to control the Turtlesim robot using the built-in `/turtle1/teleport_absolute` Service.

- Sends target coordinates (`x`, `y`) and orientation (`theta`).
- Moves the turtle to the specified position.
- Uses `turtlesim/srv/TeleportAbsolute`.
- Verifies the updated position through the `/turtle1/pose` Topic.

This demonstrates how Service communication can be used to execute robot commands while Topic communication provides continuous state information.

## How to Run

Activate the ROS2 environment and navigate to the practice directory.

```bash
ros2_study
cd ~/ros2_practice/03_service_client
```

### 03-1. AddTwoInts

Terminal 1 — Start the Server:

```bash
python3 service_server.py
```

Terminal 2 — Run the Client:

```bash
python3 service_client.py 10 20
```

Expected result:

```text
Result: 10 + 20 = 30
```

### 03-2. Turtlesim Teleport

Terminal 1 — Start Turtlesim:

```bash
ros2 run turtlesim turtlesim_node
```

Terminal 2 — Run the Client:

```bash
python3 turtle_teleport.py 8.0 8.0 0.0
```

The turtle moves to the specified coordinates and orientation.

## Useful ROS2 Commands

```bash
# List available Services
ros2 service list

# Check a Service type
ros2 service type /add_two_ints

# Inspect a Service interface
ros2 interface show example_interfaces/srv/AddTwoInts

# Call a Service directly
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 15}"

# Check the turtle's position
ros2 topic echo /turtle1/pose
```

## What I Learned

- Differences between Topic and Service communication
- Request-response communication in ROS2
- Creating Service Servers and Clients using `rclpy`
- Handling asynchronous Service requests
- Using built-in ROS2 Services for robot control
- Combining Service commands with Topic-based state monitoring

## Conclusion

Successfully implemented ROS2 Service/Client communication and controlled a Turtlesim robot through Service requests.

This practice provides a foundation for implementing command-based control in future ROS2 robotic systems.