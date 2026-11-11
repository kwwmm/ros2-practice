# 02. ROS2 Turtlesim Control — Code Analysis

## 1. 분석 대상

이번 문서에서는 ROS2 Turtlesim 시뮬레이터를 제어하기 위해 작성한 두 개의 Python 파일을 분석한다.

```text
02_turtlesim_control/
├── turtle_controller.py
├── turtle_pose.py
├── README.md
└── CODE_WALKTHROUGH.md
```

| File | 역할 |
|---|---|
| `turtle_controller.py` | 속도 명령을 발행하여 거북이를 움직이는 Publisher |
| `turtle_pose.py` | 거북이의 위치와 방향을 수신하는 Subscriber |

분석 목표:

- Python 클래스와 객체의 동작 이해
- `rclpy`를 이용한 ROS2 노드 생성 및 실행
- `geometry_msgs/msg/Twist` 메시지 구조 이해
- 선속도와 각속도가 거북이의 움직임에 미치는 영향
- `turtlesim/msg/Pose` 메시지 처리
- Timer와 Subscription Callback의 실행 과정
- 노드 초기화부터 종료까지의 전체 실행 흐름

---

## 2. turtle_controller.py 전체 코드

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')

        # Publisher: send velocity commands
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Publish every 0.1 seconds
        self.timer = self.create_timer(
            0.1,
            self.move_turtle
        )

    def move_turtle(self):
        msg = Twist()

        # Linear velocity
        msg.linear.x = 2.0

        # Angular velocity
        msg.angular.z = 1.0

        self.publisher.publish(msg)

    def stop_turtle(self):
        self.publisher.publish(Twist())


def main():
    rclpy.init()
    node = TurtleController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_turtle()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

## 3. turtle_controller.py 상세 분석

### 3.1 라이브러리 Import

```python
import rclpy
```

- `rclpy`는 ROS2의 Python 클라이언트 라이브러리다.
- 노드 초기화, 메시지 통신, Callback 실행 등을 처리한다.
- ROS2 Python 프로그램에서는 일반적으로 사용되는 라이브러리다.

```python
from rclpy.node import Node
```

- `Node` 클래스를 가져온다.
- 사용자 정의 ROS2 노드를 만들 때 상속받는 기본 클래스다.
- `create_publisher()`, `create_timer()`, `get_logger()` 등의 메서드를 제공한다.

```python
from geometry_msgs.msg import Twist
```

- `geometry_msgs` 패키지에서 `Twist` 메시지 클래스를 가져온다.
- `Twist`는 선속도와 각속도를 표현하는 ROS2 메시지 타입이다.
- 이번 실습에서는 거북이의 이동 명령을 전달하는 데 사용한다.

첫 번째 실습에서는 `String` 메시지를 사용했다.

이번에는 문자열 대신 속도 명령이 필요하므로 `Twist`를 사용한다.

### 3.2 클래스 정의

```python
class TurtleController(Node):
```

구성 요소:

| 코드 | 의미 |
|---|---|
| `class` | 새로운 클래스 정의 |
| `TurtleController` | 사용자 정의 클래스 이름 |
| `(Node)` | ROS2 Node 클래스를 상속 |
| `:` | 클래스 본문 시작 |

`TurtleController`는 `Node`를 상속받기 때문에 별도로 구현하지 않아도 ROS2 노드의 기능을 사용할 수 있다.

### 3.3 생성자와 노드 초기화

```python
def __init__(self):
    super().__init__('turtle_controller')
```

**`__init__(self)`**

- 객체가 생성될 때 실행되는 초기화 메서드다.
- Publisher와 Timer 등을 생성하는 데 사용한다.

**`self`**

- 현재 생성된 `TurtleController` 객체를 참조한다.
- 객체 내부에서 여러 메서드가 동일한 Publisher와 Timer에 접근할 수 있도록 한다.

**`super().__init__('turtle_controller')`**

- 부모 클래스인 `Node`의 생성자를 호출한다.
- ROS2 노드 이름을 `turtle_controller`로 설정한다.

다음 코드가 실행되면:

```python
node = TurtleController()
```

`__init__()`이 호출되고 ROS2 노드가 초기화된다.

실행 중인 노드는 다음 명령어로 확인할 수 있다.

```bash
ros2 node list
```

예상 노드 이름:

```text
/turtle_controller
```

### 3.4 Publisher 객체 생성

```python
self.publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

`create_publisher()`는 지정한 Topic에 메시지를 발행하는 Publisher 객체를 생성한다.

| 요소 | 의미 |
|---|---|
| `self.publisher` | Publisher 객체를 저장하는 인스턴스 속성 |
| `Twist` | 발행할 메시지 타입 |
| `'/turtle1/cmd_vel'` | 속도 명령을 전달할 Topic |
| `10` | QoS History Depth |

**`self.publisher`**

- Publisher 객체를 저장한다.
- 이후 다른 메서드에서 `self.publisher.publish()`로 접근할 수 있다.

**`Twist`**

- `geometry_msgs/msg/Twist` 메시지 타입이다.
- 선속도와 각속도를 포함한다.

**`'/turtle1/cmd_vel'`**

- Turtlesim이 속도 명령을 수신하는 Topic이다.
- `/`로 시작하는 절대 Topic 이름이다.
- `cmd_vel`은 일반적으로 command velocity를 의미한다.

**`10`**

- 기본 QoS 프로파일의 History Depth를 설정한다.
- Keep Last 정책에 따라 최대 10개의 메시지 샘플을 History에 유지한다.
- 메시지 발행 주기 10Hz를 의미하지 않는다.

`create_publisher()`는 Publisher를 생성하지만, 이 코드만으로 거북이가 움직이지는 않는다.

실제 이동 명령은 `publish()`를 호출할 때 발행된다.

### 3.5 Timer 생성

```python
self.timer = self.create_timer(
    0.1,
    self.move_turtle
)
```

`create_timer()`는 일정한 시간 간격으로 Callback이 실행되도록 Timer를 생성한다.

**첫 번째 인자: `0.1`**

- Timer 실행 간격이다.
- 단위는 초다.
- 약 0.1초마다 Callback 실행이 준비된다.

**두 번째 인자: `self.move_turtle`**

- Timer가 호출할 메서드를 지정한다.
- 함수 이름 뒤에 `()`가 없으므로 함수 객체를 전달한다.

다음 두 코드는 다르다.

```python
self.move_turtle
```

함수 객체를 참조한다.

```python
self.move_turtle()
```

함수를 즉시 호출한다.

**`self.timer`**

- 생성한 Timer 객체를 인스턴스 속성에 저장한다.

Timer 주기와 실행 빈도의 관계는 다음과 같다.

$$
f = \frac{1}{T}
$$

현재 설정에서는:

$$
f = \frac{1}{0.1} = 10 \text{ Hz}
$$

따라서 이론적으로 1초에 약 10번 이동 명령을 발행한다.

실제 주기는 시스템 부하와 Executor의 스케줄링에 따라 달라질 수 있다.

### 3.6 이동 Callback 정의

```python
def move_turtle(self):
```

- `move_turtle()`이라는 메서드를 정의한다.
- Timer에 등록된 Callback이다.
- Timer 실행 준비 이벤트가 처리될 때 호출된다.

함수 내부에서는 새로운 속도 메시지를 만들고 발행한다.

### 3.7 Twist 메시지 객체 생성

```python
msg = Twist()
```

- `Twist` 클래스의 새로운 메시지 객체를 생성한다.
- `msg`는 해당 객체를 참조하는 지역 변수다.
- `Twist()`는 기본적으로 모든 속도 성분이 0으로 초기화된다.

`Twist` 메시지는 두 개의 벡터로 구성된다.

```text
Twist
│
├── linear
│   ├── x
│   ├── y
│   └── z
│
└── angular
    ├── x
    ├── y
    └── z
```

각 벡터에는 세 가지 성분이 존재한다.

- `linear`: 병진 운동 속도
- `angular`: 회전 운동 속도

이번 실습에서는 `linear.x`와 `angular.z`만 사용한다.

### 3.8 선속도 설정

```python
msg.linear.x = 2.0
```

이 코드를 단계별로 살펴보면:

| 코드 | 의미 |
|---|---|
| `msg` | Twist 메시지 객체 |
| `.linear` | 선속도 벡터 |
| `.x` | X축 방향 선속도 |
| `= 2.0` | 해당 성분에 2.0 저장 |

Turtlesim에서는 `linear.x`가 거북이가 바라보는 방향의 전진 속도를 의미한다.

- 양수: 전진
- 음수: 후진
- 0: 선형 이동 없음

현재 설정은 전진 속도 2.0 simulation units/s를 의미한다.

중요한 점은 `linear.x`가 화면의 X축 좌표를 직접 증가시키는 명령은 아니라는 것이다.

거북이의 현재 방향에 따라 실제 X, Y 좌표 변화가 달라진다.

### 3.9 각속도 설정

```python
msg.angular.z = 1.0
```

구성 요소:

| 코드 | 의미 |
|---|---|
| `msg` | Twist 메시지 객체 |
| `.angular` | 각속도 벡터 |
| `.z` | Z축 회전 각속도 |
| `= 1.0` | 각속도를 1.0 rad/s로 설정 |

Turtlesim은 2차원 평면에서 이동한다.

따라서 회전은 평면에 수직인 Z축을 기준으로 표현한다.

- 양수: 반시계방향 회전
- 음수: 시계방향 회전
- 0: 회전하지 않음

현재 각속도는 1.0 rad/s이다.

이를 도 단위로 환산하면:

$$
1 \text{ rad/s} \approx 57.3^\circ/\text{s}
$$

즉, 거북이는 전진하면서 초당 약 57.3도씩 반시계방향으로 회전하도록 명령받는다.

### 3.10 원형 이동이 발생하는 이유

```python
msg.linear.x = 2.0
msg.angular.z = 1.0
```

두 명령이 동시에 적용되기 때문이다.

- `linear.x`: 거북이를 앞으로 이동시킨다.
- `angular.z`: 거북이의 진행 방향을 지속적으로 변경한다.

전진 방향이 계속 회전하면 곡선 경로가 만들어진다.

선속도와 각속도가 일정한 이상적인 평면 운동에서는 원형 경로가 형성된다.

회전 반지름은 다음과 같다.

$$
R = \frac{|v|}{|\omega|}
$$

현재 설정에서는:

$$
R = \frac{2.0}{1.0} = 2.0
$$

따라서 이론적인 회