
# ROS2 Jazzy Practice

ROS2 Jazzy를 활용한 Python 기반 로봇 프로그래밍 실습 기록입니다.

## Environment

- Ubuntu 24.04 LTS
- ROS2 Jazzy
- Python 3.12

## Practice List

| No. | Topic | Description |
|---|---|---|
| 01 | Publisher & Subscriber | ROS2 Topic 통신 기초 |

## 01. Publisher & Subscriber

### Objective
- ROS2 Node 개념 이해
- Publisher와 Subscriber 구현
- Topic을 통한 메시지 송수신

### Files
- `publisher.py`: 1초마다 메시지 발행
- `subscriber.py`: 메시지 수신 및 출력

### Communication

Publisher → `/my_topic` → Subscriber

Message Type: `std_msgs/msg/String`

### How to Run

Terminal 1:
```bash
ros2_study
cd ~/ros2_practice/01_publisher_subscriber
python3 publisher.py
```

Terminal 2:
```bash
ros2_study
cd ~/ros2_practice/01_publisher_subscriber
python3 subscriber.py
```

### Useful Commands

```bash
ros2 node list
ros2 topic list
ros2 topic echo /my_topic
ros2 topic hz /my_topic
rqt_graph
```

### What I Learned

- Node는 ROS2 프로그램의 실행 단위이다.
- Publisher는 Topic에 메시지를 발행한다.
- Subscriber는 Topic을 구독하여 메시지를 받는다.
- Topic 이름과 메시지 타입이 일치해야 통신할 수 있다.
