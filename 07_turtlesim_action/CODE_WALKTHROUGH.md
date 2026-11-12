# CODE_WALKTHROUGH — 실습 07: Turtlesim Action 기반 목표 좌표 이동

> 코드 기준: 이 대화에서 제시하고 사용자가 실행한 `move_server.py`, `move_client.py`, `MoveToGoal.action` 및 인터페이스 설정 예시. 실제 Ubuntu 로컬 파일을 직접 열어 최신 내용을 대조한 것은 아니므로, 로컬에서 추가 변경한 부분이 있다면 아래 내용과 차이가 있을 수 있다. 확인된 실행 결과는 뒤의 해당 코드 해설에 따로 표시했다.

## 1. `move_server.py` 전체 코드

```python
import math
import time
import threading

import rclpy
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_move_interfaces.action import MoveToGoal


class TurtleMoveServer(Node):

    def __init__(self):
        super().__init__('turtle_move_server')

        self.current_pose = None
        self.goal_active = False
        self.goal_lock = threading.Lock()

        self.callback_group = ReentrantCallbackGroup()

        self.velocity_publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.pose_subscriber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.callback_group
        )

        self.action_server = ActionServer(
            self,
            MoveToGoal,
            'move_to_goal',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('Turtle Move Action Server started.')

    def pose_callback(self, msg):
        self.current_pose = msg

    def goal_callback(self, goal_request):
        x = goal_request.target_x
        y = goal_request.target_y

        if not (
            math.isfinite(x)
            and math.isfinite(y)
            and 0.5 <= x <= 10.5
            and 0.5 <= y <= 10.5
        ):
            self.get_logger().warn('Invalid target position.')
            return GoalResponse.REJECT

        with self.goal_lock:
            if self.goal_active:
                self.get_logger().warn('Another goal is active.')
                return GoalResponse.REJECT

            self.goal_active = True

        self.get_logger().info(
            f'Goal received: ({x:.2f}, {y:.2f})'
        )

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received.')
        return CancelResponse.ACCEPT

    def stop_turtle(self):
        self.velocity_publisher.publish(Twist())

    def execute_callback(self, goal_handle):
        target_x = goal_handle.request.target_x
        target_y = goal_handle.request.target_y

        feedback = MoveToGoal.Feedback()
        result = MoveToGoal.Result()

        result.success = False
        start_time = time.monotonic()

        self.get_logger().info('Moving to target...')

        try:
            while rclpy.ok():

                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.get_logger().info('Goal canceled.')
                    break

                if time.monotonic() - start_time >= 60.0:
                    goal_handle.abort()
                    self.get_logger().warn('Goal timeout.')
                    break

                if self.current_pose is None:
                    time.sleep(0.1)
                    continue

                x = self.current_pose.x
                y = self.current_pose.y
                theta = self.current_pose.theta

                dx = target_x - x
                dy = target_y - y

                distance = math.hypot(dx, dy)

                target_angle = math.atan2(dy, dx)

                angle_error = math.atan2(
                    math.sin(target_angle - theta),
                    math.cos(target_angle - theta)
                )

                feedback.current_x = x
                feedback.current_y = y
                feedback.distance_remaining = distance

                goal_handle.publish_feedback(feedback)

                if distance < 0.15:
                    self.stop_turtle()
                    goal_handle.succeed()
                    result.success = True
                    self.get_logger().info('Goal reached.')
                    break

                cmd = Twist()

                if abs(angle_error) > 0.35:
                    cmd.linear.x = 0.0
                else:
                    cmd.linear.x = min(1.5, distance)

                cmd.angular.z = max(
                    -2.0,
                    min(2.0, 4.0 * angle_error)
                )

                self.velocity_publisher.publish(cmd)

                time.sleep(0.1)

            if goal_handle.is_active:
                goal_handle.abort()

        finally:
            self.stop_turtle()

            if self.current_pose is not None:
                result.final_x = self.current_pose.x
                result.final_y = self.current_pose.y

            with self.goal_lock:
                self.goal_active = False

        return result


def main(args=None):
    rclpy.init(args=args)

    node = TurtleMoveServer()

    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_turtle()
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

## 2. `move_server.py` 코드 순서대로 해설

### 2.1 `import`: 파일 맨 위의 모듈과 객체

```python
import math
import time
import threading
```

- `import`는 Python 모듈을 현재 파일에서 사용할 수 있게 하는 문법이다. `math`라는 이름으로 모듈을 가져오므로 `math.atan2(...)`처럼 점(`.`)으로 내부 함수를 찾는다.
- `math.hypot(dx, dy)`는 두 좌표 차이로부터 유클리드 거리를 구한다. `math.atan2(y, x)`는 **인자를 `(y, x)` 순서로** 받는다는 점이 중요하다. `math.sin`, `math.cos`는 각도 차이를 `[-π, π]` 근처로 정규화할 때 쓴다. `math.isfinite`는 `NaN`, 무한대를 거부한다.
- `time.monotonic()`은 시스템 시각 변경에 영향을 받지 않는 경과 시간 측정용 시계를 읽는다. 단위는 초이며 반환값은 `float`다. `time.sleep(0.1)`은 현재 실행 중인 스레드를 약 0.1초 동안 쉬게 한다. 정확한 실시간 주기를 보장하지 않는다.
- `threading.Lock()`은 여러 스레드에서 공유하는 `goal_active`를 보호하는 잠금 객체다. `with self.goal_lock:`으로 잠금을 획득하고 블록에서 벗어날 때 해제한다. 다만 현재 코드의 잠금은 `goal_active`의 일부 접근만 보호하며, Pose 객체나 모든 상태를 원자적으로 보호하지는 않는다.

```python
import rclpy
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
```

- `rclpy`는 ROS 2의 Python 클라이언트 라이브러리다. `rclpy.init()`은 ROS 2 실행 컨텍스트를 초기화하고, `rclpy.ok()`는 해당 컨텍스트가 활성 상태인지 검사한다.
- `from ... import ...`는 모듈 내부의 이름만 현재 네임스페이스로 가져오는 문법이다. `ActionServer`는 목표 수락·실행·결과·취소를 관리하며, `GoalResponse`와 `CancelResponse`는 각 요청에 대한 응답 선택값을 제공한다.
- `ReentrantCallbackGroup`은 같은 콜백 그룹에 속한 콜백들이 동시에 실행되는 것을 허용한다. 반드시 동시에 실행된다는 뜻은 아니다. 여러 스레드를 가진 Executor와 결합해야 이점이 있다.
- `MultiThreadedExecutor`는 준비된 콜백들을 여러 작업 스레드로 실행할 수 있다. 이 코드에서 `num_threads=3`으로 설정했다.
- `Node`는 ROS 2 노드의 기본 클래스다. `TurtleMoveServer(Node)`라는 상속 문법을 통해 로거, 퍼블리셔, 서브스크립션 등을 만드는 기능을 물려받는다.

```python
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_move_interfaces.action import MoveToGoal
```

- `Twist`는 선속도(`linear`)와 각속도(`angular`)를 담는 메시지다. 여기서는 `linear.x`와 `angular.z`만 바꾼다. 각각 Turtlesim의 전진 속도와 회전 속도 명령에 사용된다.
- `Pose`는 Turtlesim이 발행하는 현재 위치·방향·속도 정보다. `x`, `y`, `theta`를 읽는다. `theta`의 단위는 라디안이다.
- `MoveToGoal`은 사용자가 작성한 `action/MoveToGoal.action` 정의로부터 ROSIDL 빌드가 생성한 Action 타입이다. 이 타입 안에 `Goal`, `Result`, `Feedback` 메시지가 있다. `.action` 파일만 저장했다고 이 Import가 가능한 것은 아니고, `colcon build`와 환경 활성화가 필요하다.

### 2.2 클래스, 생성자, `self`, 상속

```python
class TurtleMoveServer(Node):

    def __init__(self):
        super().__init__('turtle_move_server')
```

- `class`는 객체를 생성하기 위한 설계도를 정의한다. 괄호 안의 `Node`는 부모 클래스다.
- `def __init__(self):`는 객체가 만들어질 때 호출되는 특별 메서드인 생성자다. `self`는 **지금 생성 중인 서버 객체 자신**을 가리킨다. Python은 인스턴스 메서드 호출 시 그 객체를 첫 번째 인자로 전달한다.
- `super().__init__('turtle_move_server')`는 부모 `Node`의 생성자를 실행해 ROS 노드 이름을 지정한다. `super()`는 부모 클래스를 참조하고, 괄호 뒤 `.__init__`은 그 객체의 메서드를 호출하는 문법이다.
- `TurtleMoveServer()` 객체가 한 개 만들어져야 생성자 내부의 ROS 통신 객체들도 생성된다. 클래스 선언만으로 노드가 실행되는 것은 아니다.

```python
self.current_pose = None
self.goal_active = False
self.goal_lock = threading.Lock()
self.callback_group = ReentrantCallbackGroup()
```

- `self.current_pose`는 최근 수신한 `Pose` 객체의 참조를 저장한다. 최초에는 아직 메시지가 도착하지 않았으므로 `None`이다. `None`은 Python에서 값이 없음을 나타내는 단일 객체다.
- `self.goal_active`는 이미 목표를 처리 중인지 기억하는 `bool` 값이다. 새 Goal을 무조건 수락하지 않기 위해 사용한다.
- `self.goal_lock`은 두 Goal 요청이 거의 동시에 들어오는 경우 `goal_active` 검사 및 변경을 하나의 임계구역으로 묶는다.
- `self.callback_group`을 하나 만들어 Subscription과 Action Server 모두에 연결한다. 해당 그룹이 재진입을 허용하므로 한 Goal의 실행이 길어도 Pose·Cancel 콜백을 처리할 여지가 생긴다.

### 2.3 Publisher 생성: `/turtle1/cmd_vel`

```python
self.velocity_publisher = self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

- `self.create_publisher(...)`는 Node의 메서드로 Publisher 객체를 만들어 돌려준다. 반환된 객체를 인스턴스 속성에 저장해야 이후 `publish()`를 호출할 수 있다.
- 첫 번째 인자 `Twist`는 보낼 ROS 메시지의 **타입**이며 `Twist()`라는 실제 메시지 인스턴스와 다르다.
- 두 번째 인자 `'/turtle1/cmd_vel'`은 Topic 이름을 뜻하는 문자열이다. 앞의 `/`는 전역 이름을 명시한다.
- 세 번째 인자 `10`은 기본 QoS 설정에서 깊이(depth)를 지정하는 간편 표기다. '초당 10회 발행'이 아니라 큐 설정에 관계하는 값이다.
- 이 줄에서 속도가 즉시 발행되는 것은 아니다. 퍼블리셔를 등록할 뿐이며, 실제 데이터는 `self.velocity_publisher.publish(cmd)`에서 발행된다.

### 2.4 Subscriber 생성: `/turtle1/pose`

```python
self.pose_subscriber = self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.pose_callback,
    10,
    callback_group=self.callback_group
)
```

- `create_subscription`의 인자 순서는 **메시지 타입, Topic 이름, Callback 함수, QoS depth**이며 여기서는 `callback_group`도 전달한다.
- `self.pose_callback`에는 괄호가 없다. 즉 **함수 실행 결과**가 아니라 나중에 실행할 **바운드 메서드 객체**를 전달한다. 만약 `self.pose_callback()`이라고 쓰면 즉시 호출하려 하므로 인자 `msg`가 없어 오류가 발생한다.
- Turtlesim이 `/turtle1/pose`에 `Pose`를 발행하면 Executor가 수신을 처리하고 해당 콜백을 호출할 수 있다. 생성 시점에 Callback이 바로 실행되지는 않는다.
- `self.pose_subscriber`는 Subscription 객체를 보관한다. `callback_group` 덕분에 Action 실행이 이어지는 동안에도 위치 갱신을 처리할 수 있다.

```python
def pose_callback(self, msg):
    self.current_pose = msg
```

- `msg`는 **수신된 Pose 메시지 객체**다. Python의 대입 연산자 `=`는 기본적으로 객체를 복사하지 않고 참조를 할당한다.
- 따라서 `self.current_pose`는 '마지막으로 콜백이 받은 객체'를 가리킨다. 다음 Pose가 도착하면 새 참조로 갱신된다.
- 별도 `return`이 없으므로 Python 반환값은 `None`이다. 이 콜백은 값을 반환하기 위해서가 아니라 노드의 내부 상태를 갱신하기 위해 실행된다.

### 2.5 ActionServer 생성

```python
self.action_server = ActionServer(
    self,
    MoveToGoal,
    'move_to_goal',
    execute_callback=self.execute_callback,
    goal_callback=self.goal_callback,
    cancel_callback=self.cancel_callback,
    callback_group=self.callback_group
)
```

- 첫 인자 `self`는 이 Action Server가 소속될 ROS Node다.
- `MoveToGoal`은 Goal·Result·Feedback 형태를 결정한다. 서버와 클라이언트가 같은 Action 타입 및 이름을 사용해야 한다.
- `'move_to_goal'`은 Action 이름이며 서버 노드의 현재 네임스페이스에서는 `/move_to_goal`로 보인다.
- `execute_callback`은 수락된 Goal의 작업을 실제로 수행해 **Result 객체**를 돌려준다.
- `goal_callback`은 Goal이 도착했을 때 수락/거부를 판단한다.
- `cancel_callback`은 취소 요청을 받았을 때 수락/거부를 결정한다. **취소를 허용하는 것과 실제 작업을 중단하는 것은 다른 단계**다.
- 키워드 인자 `name=value`는 인자 이름을 명시해 전달하는 Python 문법이다. `callback_group=self.callback_group`의 두 `callback_group`은 각각 함수 인자 이름과 객체 속성이다.
- 서버 구성 이후 `self.get_logger().info(...)`는 시작을 알리는 로그를 출력한다. 이는 Goal 성공이 아니라 서버 노드가 생성되었다는 뜻이다.

### 2.6 Goal 수락·거부 콜백

```python
def goal_callback(self, goal_request):
    x = goal_request.target_x
    y = goal_request.target_y
```

- `goal_request`는 `MoveToGoal.Goal` 형식의 요청 객체다. `target_x`, `target_y`는 `.action` 파일 앞부분에서 정의한 `float32` 필드다.
- `x`와 `y`는 이후 가독성을 높이기 위한 지역 변수이며 생성자에서 저장한 `self.current_pose.x`와는 다른 값이다. 이 둘을 혼동하면 안 된다.

```python
if not (
    math.isfinite(x)
    and math.isfinite(y)
    and 0.5 <= x <= 10.5
    and 0.5 <= y <= 10.5
):
    self.get_logger().warn('Invalid target position.')
    return GoalResponse.REJECT
```

- `if`는 조건이 참일 때 아래 들여쓰기 블록을 실행한다. `and`는 모든 조건이 참일 때만 참이고, `not`은 결과를 뒤집는다.
- `0.5 <= x <= 10.5`는 Python의 연쇄 비교이며 `(0.5 <= x) and (x <= 10.5)`와 같은 의미다.
- `math.isfinite` 조건은 유효한 실수 범위 검사에서 놓칠 수 있는 `NaN` 또는 무한대를 거부한다.
- `return GoalResponse.REJECT`가 실행되면 **함수를 즉시 종료**하며 이후 목표 점유 상태를 변경하지 않는다.
- 이 안전 영역은 코드의 실습용 입력 제한일 뿐, 실제 Turtlesim의 모든 경계 충돌이나 현실 로봇의 장애물을 보장하는 안전 시스템이 아니다.

```python
with self.goal_lock:
    if self.goal_active:
        self.get_logger().warn('Another goal is active.')
        return GoalResponse.REJECT
    self.goal_active = True
```

- `with`는 잠금 획득과 해제를 관리한다. `return`으로 블록을 빠져나가도 잠금은 해제된다.
- 이미 활성 목표가 있으면 새로운 요청을 거부한다. 활성 목표가 없을 때 `True`로 바꾸는 동작을 같은 잠금 구간에 넣어 동시 Goal 수락 경쟁을 줄인다.
- `goal_active=True`는 ROS 2의 Action 상태 자체가 아니라 **이 코드에서 추가한 Python 플래그**다.
- 현 코드는 Goal을 수락할 때 이 플래그를 켜고 `execute_callback`의 `finally`에서 끈다. 수락 후 실행 콜백이 비정상적으로 시작되지 못하는 예외 상황까지 모두 해결하는 견고한 목표 관리기는 아니다.

```python
self.get_logger().info(f'Goal received: ({x:.2f}, {y:.2f})')
return GoalResponse.ACCEPT
```

- `f'...'`는 f-string: 중괄호 안의 Python 표현식 값을 문자열로 넣는다. `:.2f`는 소수점 둘째 자리까지 표시하라는 형식 지정자이며 **원래 수치 자체를 반올림해 저장하지는 않는다**.
- `GoalResponse.ACCEPT`는 ROS 2에게 새 Goal을 수락한다는 의사를 전달한다. 아직 목표 위치에 도착했다는 의미는 아니다.

### 2.7 취소 수락 콜백과 정지 함수

```python
def cancel_callback(self, goal_handle):
    self.get_logger().info('Cancel request received.')
    return CancelResponse.ACCEPT
```

- `goal_handle`은 특정 목표를 가리키는 서버 측 핸들이다.
- 이 Callback은 취소 요청을 **받아들일지 결정**한다. 실제 정지 명령은 아직 보내지 않는다.
- `CancelResponse.ACCEPT`를 반환하면 ROS 2 Action 시스템에서 해당 목표를 취소 진행 대상으로 처리할 수 있다. 실제 `Goal canceled.` 최종 상태는 실행 루프에서 `goal_handle.canceled()`를 호출해야 만들어진다.

```python
def stop_turtle(self):
    self.velocity_publisher.publish(Twist())
```

- `Twist()`는 기본 필드가 0으로 초기화된 새 메시지 객체를 만든다. 따라서 이 실습에서 사용 중인 `linear.x`와 `angular.z` 역시 0이다.
- `publish()`는 토픽에 속도 명령을 한 번 발행한다. Turtlesim이 해당 메시지를 수신하면 거북이 이동/회전 명령이 0이 된다.
- 이 함수는 도착 판정 시, 실행 종료의 `finally`, 노드 종료 시 호출된다. 독립 실행 코드 중복을 피하기 위한 작은 메서드다.

### 2.8 `execute_callback` 시작: Goal·Feedback·Result 객체

```python
def execute_callback(self, goal_handle):
    target_x = goal_handle.request.target_x
    target_y = goal_handle.request.target_y

    feedback = MoveToGoal.Feedback()
    result = MoveToGoal.Result()

    result.success = False
    start_time = time.monotonic()
```

- `execute_callback`은 승인한 Goal의 실제 장시간 작업을 수행한다. `goal_handle.request`는 이 Goal의 Request 메시지이고, 그 안에 요청한 목표 좌표가 있다.
- `MoveToGoal.Feedback()`와 `MoveToGoal.Result()`는 **클래스로부터 새 메시지 인스턴스를 생성**하는 문법이다. `Feedback`은 중간 업데이트용이고 `Result`는 마지막 응답용이다.
- `result.success = False`로 기본 실패를 설정한다. 목표에 실제로 도착한 경우에만 `True`로 변경한다.
- `start_time`은 상대 경과 시간을 측정하는 기준값이며, 이 메서드가 시작한 뒤 한 번만 저장한다.

### 2.9 반복 실행 루프와 취소·타임아웃

```python
try:
    while rclpy.ok():
```

- `try`는 예외 여부와 무관하게 아래의 `finally`에서 정지 명령을 실행하기 위한 제어 구조다.
- `while`은 조건이 참인 동안 반복한다. 여기서는 ROS 2 컨텍스트가 유지되는 동안 제어 명령을 계산한다.
- 현재 코드에는 `time.sleep(0.1)`이 있으므로 계속 바쁘게 반복하는 순수 busy loop는 아니지만, 실행 스레드 한 개는 그동안 점유한다.

```python
if goal_handle.is_cancel_requested:
    goal_handle.canceled()
    self.get_logger().info('Goal canceled.')
    break
```

- `is_cancel_requested`는 해당 Goal에 취소 요청이 들어왔는지 나타내는 상태 속성이다.
- `goal_handle.canceled()`는 그 Goal을 취소 완료 상태로 전환한다. 이어서 `break`가 **가장 안쪽 `while` 반복문**을 종료한다.
- 이 부분이 없으면 `cancel_callback`이 요청을 받아들여도 실제 이동 루프는 계속될 수 있다.

```python
if time.monotonic() - start_time >= 60.0:
    goal_handle.abort()
    self.get_logger().warn('Goal timeout.')
    break
```

- 현재 단조 시간에서 시작 시간을 빼 경과 초를 구한다.
- 60초 이상이면 `abort()`로 실패 종료 상태를 설정하고 루프를 끝낸다. `abort()`와 `canceled()`는 서로 다른 Action 종료 상태다.
- `>=`는 '크거나 같다' 연산자다. `60.0`은 `float` 리터럴이며 단위는 초다.

```python
if self.current_pose is None:
    time.sleep(0.1)
    continue
```

- Pose 메시지가 아직 수신되지 않았다면 계산할 현재 위치가 없으므로 잠시 기다린다.
- `continue`는 **현재 반복 회차의 나머지 코드를 생략**하고 다음 `while` 검사로 이동한다. `break`는 반복문을 완전히 종료한다는 차이가 있다.

### 2.10 현재 위치와 위치 오차

```python
x = self.current_pose.x
y = self.current_pose.y
theta = self.current_pose.theta

dx = target_x - x
dy = target_y - y

distance = math.hypot(dx, dy)
```

- 현재 위치는 Subscription Callback이 갱신한 최근 Pose 객체에서 읽는다.
- `x`, `y`는 위치 좌표, `theta`는 방향각(라디안)이다. Python 변수의 자료형은 값에 따라 결정되고, 보통 해당 ROS 필드는 실수형으로 처리된다.
- `dx`, `dy`는 목표 좌표에서 현재 좌표를 뺀 **오차 성분**이다. 예를 들어 현재가 `(5.54, 5.54)`, 목표가 `(8, 8)`이라면 `dx≈2.46`, `dy≈2.46`이다.
- `math.hypot(dx, dy)`는 `sqrt(dx**2 + dy**2)`와 같은 기하학적 거리를 계산한다. `**`는 Python의 거듭제곱 연산자다.
- 실제 수행 로그에서 처음 거리는 약 `3.47`로 출력되었다.

### 2.11 목표 방향과 방향 오차 정규화

```python
target_angle = math.atan2(dy, dx)

angle_error = math.atan2(
    math.sin(target_angle - theta),
    math.cos(target_angle - theta)
)
```

- `target_angle`은 현재 위치에서 목표 위치를 향하는 벡터의 방향각이다.
- 단순 `target_angle - theta`는 `π` 경계에서 거의 한 바퀴 차이처럼 표현될 수 있다. 예를 들어 현재 방향이 `179°`, 목표 방향이 `-179°`라면 단순 차는 `-358°`지만 실제 가장 짧은 회전은 `2°`다.
- `atan2(sin(Δ), cos(Δ))`는 각도차를 약 `[-π, π]` 범위로 접어 주어 짧은 방향 회전을 가능하게 한다. 이는 위치를 정규화하는 것이 아니라 **각도 오차만 정규화**한다.
- 줄바꿈한 함수 호출의 괄호 안에서는 Python이 개행을 허용한다. 쉼표는 첫 번째 인자와 두 번째 인자를 구분한다.

### 2.12 Feedback 생성과 전송

```python
feedback.current_x = x
feedback.current_y = y
feedback.distance_remaining = distance

goal_handle.publish_feedback(feedback)
```

- `feedback`은 반복마다 새로 만드는 것이 아니라 루프 시작 전에 한 번 생성한 객체를 매번 업데이트한다.
- 세 필드는 `.action` 파일의 Feedback 부분에서 선언한 이름과 일치해야 한다. 이름 또는 자료형이 맞지 않으면 런타임 오류가 발생할 수 있다.
- `publish_feedback`은 현재 Goal에 연결된 Client로 중간 데이터를 전송한다. 클라이언트에서는 `feedback_callback`이 나중에 실행된다.
- **피드백을 보냈다는 사실이 Goal 성공을 뜻하지 않는다.** 상태 통지와 작업 종료는 별개다.

### 2.13 목표 도달 판정

```python
if distance < 0.15:
    self.stop_turtle()
    goal_handle.succeed()
    result.success = True
    self.get_logger().info('Goal reached.')
    break
```

- Turtlesim 좌표계에서 목표와의 거리가 `0.15` 미만이면 도착으로 간주한다. 정확히 `(8.0, 8.0)`과 같을 필요는 없다.
- 먼저 정지 명령을 발행하고, `succeed()`로 Action 상태를 성공으로 전환하고, 사용자 정의 `result.success` 필드를 `True`로 설정한다.
- `break` 이후에도 `finally`가 실행되므로 정지 명령이 한 번 더 발행될 수 있다. 안전한 중복 정지이지만 최적화된 제어 구조라고 볼 필요는 없다.
- 실제 결과에서 마지막 Feedback 거리는 `0.14`, 최종 위치는 `(7.99, 7.86)`이므로 설정한 성공 기준과 일치한다.

### 2.14 P 제어의 속도 명령 생성

```python
cmd = Twist()

if abs(angle_error) > 0.35:
    cmd.linear.x = 0.0
else:
    cmd.linear.x = min(1.5, distance)
```

- `Twist()`로 새 속도 명령 메시지를 만든다. `abs`는 절댓값을 구하는 Python 내장 함수다.
- 방향 오차의 절댓값이 `0.35 rad`보다 크면 전진 명령을 0으로 만들어 **먼저 회전**한다. `0.35 rad`는 약 `20°`다.
- 그렇지 않으면 현재 거리 `distance`를 선속도에 비례시키되 `min(1.5, distance)`로 최대값을 1.5로 제한한다.
- `min(a, b)`는 두 값 중 작은 값을 반환한다. 이 경우 목표에 가까워질수록 선속도 명령이 줄어드는 단순 비례 제어다.
- `cmd.linear.x`는 메시지 필드 할당이며, 아래 `publish()`를 호출하기 전까지는 Turtlesim에 영향을 주지 않는다.

```python
cmd.angular.z = max(
    -2.0,
    min(2.0, 4.0 * angle_error)
)
```

- 방향 오차에 비례 이득 `Kp=4.0`을 곱해 각속도 명령을 계산한다.
- 내부 `min(2.0, 값)`은 상한을 +2.0으로 제한하고, 외부 `max(-2.0, 값)`은 하한을 -2.0으로 제한한다. 즉 `[-2.0, 2.0]`로 포화(saturation)시킨다.
- `angular.z`의 양·음 부호는 회전 방향을 결정한다. 각속도 단위는 rad/s로 해석한다.
- 코드 전체에 누적 오차 적분이나 오차 변화량 미분은 없으므로 **PID가 아니라 P 기반의 단순 제어기**다.

```python
self.velocity_publisher.publish(cmd)
time.sleep(0.1)
```

- `publish(cmd)`가 실제 속도 명령을 Topic에 보내는 시점이다. 이후 Turtlesim이 해당 메시지를 받고 움직이며 새로운 Pose를 발행한다.
- `sleep(0.1)`은 대략 10Hz 주기로 실행하려는 의도이지만 Python 스케줄링, 콜백 지연, 통신 시간 때문에 실제 주기가 정확히 0.1초가 아닐 수 있다.
- 실제 Client 로그에서는 Feedback 시각 간격이 불규칙하게 나타났고 몇 번은 같은 위치가 반복되었다. 이는 관찰된 현상이며, 로그만으로 단일 원인을 확정할 수는 없다.

### 2.15 반복 종료·자원 정리·반환

```python
if goal_handle.is_active:
    goal_handle.abort()
```

- `while`이 ROS 종료 등으로 끝났는데 Goal이 여전히 활성이라면 `abort()`로 종료 상태를 설정하려는 방어 코드다.
- 성공·취소·타임아웃 분기에서는 이미 종료 상태가 되었으므로 일반적으로 이 조건은 거짓이다.

```python
finally:
    self.stop_turtle()

    if self.current_pose is not None:
        result.final_x = self.current_pose.x
        result.final_y = self.current_pose.y

    with self.goal_lock:
        self.goal_active = False

return result
```

- `finally`는 정상적인 `break`뿐 아니라 예외로 `try` 블록을 빠져나갈 때도 실행된다. 따라서 최소한 정지 명령과 `goal_active` 초기화를 시도한다.
- `result.final_x`, `result.final_y`에 마지막으로 수신한 Pose를 기록한다. 따라서 이것은 **서버에서 마지막으로 관측한 위치**이지 완벽한 실시간 정지 순간을 보증하는 측정값은 아니다.
- `goal_active=False`로 돌려놓아 다음 Goal을 수락할 수 있게 한다. `with` 구문은 여러 스레드에서 플래그를 변경하는 구간을 보호한다.
- 마지막 `return result`로 Action 타입에 맞는 Result 메시지 객체를 돌려준다. 클라이언트는 `get_result_async()`로 기다리던 결과를 받는다.
- 잠재적 한계: `try` 내부에서 처리되지 않은 예외가 생기면 `finally`는 실행되지만 그 예외가 전파되어 명시적 `abort()` 및 정상 Result 반환에 실패할 수 있다. 실제 로봇용 코드에서는 예외 처리와 watchdog을 더 강화해야 한다.

### 2.16 `main()`과 프로그램 생명주기

```python
def main(args=None):
    rclpy.init(args=args)
    node = TurtleMoveServer()

    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)
```

- `def main(args=None)`은 실행 진입 함수 정의다. 기본 인자 `None`은 호출할 때 별도의 ROS 인자를 넘기지 않아도 되게 한다.
- `rclpy.init(args=args)`는 ROS Context를 준비한다. 초기화 전에는 일반적인 ROS 노드 생성이 정상적으로 작동하지 않는다.
- `node = TurtleMoveServer()`는 클래스 인스턴스를 만들어 `__init__()`을 실제로 실행한다. 즉 Publisher, Subscriber, ActionServer도 이때 만들어진다.
- `MultiThreadedExecutor(num_threads=3)`는 세 작업 스레드로 Callback을 처리할 수 있는 Executor 객체를 만든다. `add_node(node)`를 호출해야 이 Executor가 이 노드의 콜백을 처리한다.

```python
try:
    executor.spin()
except KeyboardInterrupt:
    pass
finally:
    node.stop_turtle()
    executor.shutdown()
    node.destroy_node()
    rclpy.try_shutdown()
```

- `executor.spin()`은 일반적으로 종료 요청 전까지 블로킹하며 노드의 Callback을 처리한다. 이 코드에서 실행 중인 메인 스레드는 Executor를 돌리는 역할을 한다.
- `except KeyboardInterrupt`는 `Ctrl+C`로 종료할 때 발생할 수 있는 인터럽트를 처리한다. `pass`는 아무 작업도 하지 않는 문장이다.
- `finally`에서 정지 명령을 발행한 후 Executor와 Node를 해제하고 ROS 컨텍스트 종료를 시도한다.
- `try_shutdown()`은 이미 종료된 상황에서도 안전하게 종료를 시도하도록 한 API다.

```python
if __name__ == '__main__':
    main()
```

- Python은 파일을 직접 실행할 때 전역 변수 `__name__`을 `'__main__'`으로 설정한다. 따라서 `python3 move_server.py`라면 조건이 참이어서 `main()`을 호출한다.
- 다른 파일에서 `import move_server`로 불러온 경우 이 조건은 일반적으로 거짓이다. 클래스와 함수를 정의할 뿐 서버를 자동 시작하지 않는다.

## 3. `move_client.py` 전체 코드

```python
import argparse
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from action_msgs.msg import GoalStatus
from turtle_move_interfaces.action import MoveToGoal


class TurtleMoveClient(Node):

    def __init__(self, cancel_after=0.0):
        super().__init__('turtle_move_client')

        self.action_client = ActionClient(
            self,
            MoveToGoal,
            'move_to_goal'
        )

        self.goal_handle = None
        self.finished = False

        self.cancel_after = cancel_after
        self.cancel_sent = False
        self.start_time = None

    def send_goal(self, x, y):
        goal_msg = MoveToGoal.Goal()

        goal_msg.target_x = float(x)
        goal_msg.target_y = float(y)

        self.get_logger().info('Waiting for Action Server...')

        self.action_client.wait_for_server()

        self.start_time = time.monotonic()

        self.send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self.send_goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):
        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().warn('Goal rejected.')
            self.finished = True
            return

        self.get_logger().info('Goal accepted.')

        self.result_future = self.goal_handle.get_result_async()

        self.result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback

        self.get_logger().info(
            f'Position: ({feedback.current_x:.2f}, '
            f'{feedback.current_y:.2f}) | '
            f'Distance: {feedback.distance_remaining:.2f}'
        )

        if (
            self.cancel_after > 0
            and not self.cancel_sent
            and self.goal_handle is not None
            and time.monotonic() - self.start_time
            >= self.cancel_after
        ):
            self.cancel_sent = True

            self.get_logger().info('Sending cancel request...')

            cancel_future = self.goal_handle.cancel_goal_async()

            cancel_future.add_done_callback(
                self.cancel_response_callback
            )

    def cancel_response_callback(self, future):
        response = future.result()

        if response.goals_canceling:
            self.get_logger().info('Cancel accepted.')
        else:
            self.get_logger().warn('Cancel not accepted.')

    def result_callback(self, future):
        response = future.result()

        result = response.result
        status = response.status

        self.get_logger().info(
            f'Final position: '
            f'({result.final_x:.2f}, {result.final_y:.2f})'
        )

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Goal succeeded.')

        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info('Goal canceled.')

        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().warn('Goal aborted.')

        else:
            self.get_logger().warn(f'Goal status: {status}')

        self.finished = True


def main(args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('x', type=float)
    parser.add_argument('y', type=float)

    parser.add_argument(
        '--cancel-after',
        type=float,
        default=0.0
    )

    parsed_args = parser.parse_args()

    rclpy.init(args=args)

    node = TurtleMoveClient(
        cancel_after=parsed_args.cancel_after
    )

    try:
        node.send_goal(parsed_args.x, parsed_args.y)

        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

## 4. `move_client.py` 코드 순서대로 해설

### 4.1 Import와 클라이언트 객체 생성

```python
import argparse
import time
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from turtle_move_interfaces.action import MoveToGoal
```

- `argparse`는 터미널 인자를 해석하는 Python 표준 라이브러리다. 예를 들어 `python3 move_client.py 8 8 --cancel-after 3`의 좌표와 옵션을 자료형에 맞게 읽는다.
- `time.monotonic()`은 취소 요청을 보내기까지의 경과 시간을 계산한다.
- `ActionClient`는 Goal 전송·Feedback 수신·결과 수신·취소 요청을 처리한다.
- `GoalStatus`는 `STATUS_SUCCEEDED`, `STATUS_CANCELED`, `STATUS_ABORTED` 같은 Action 상태 상수를 제공한다.
- Import한 `MoveToGoal`은 서버가 사용하는 것과 같은 사용자 정의 Action 인터페이스다.

```python
class TurtleMoveClient(Node):
    def __init__(self, cancel_after=0.0):
        super().__init__('turtle_move_client')
```

- 이 클래스 역시 `Node`를 상속한다. `__init__`의 `cancel_after=0.0`은 기본 인자다. 사용자가 따로 지정하지 않으면 0.0이 적용되어 자동 취소를 하지 않는다.
- 서버와 클라이언트는 **서로 다른 프로세스에서 생성되는 별도 노드**이며, Python의 `self`도 각 인스턴스에 따라 완전히 다르다.

```python
self.action_client = ActionClient(
    self,
    MoveToGoal,
    'move_to_goal'
)
```

- Node, Action 타입, Action 이름이 각각 첫째·둘째·셋째 인자로 전달된다. 서버의 Action 이름과 동일해야 연결된다.
- 이 생성자는 Client 객체를 등록한다. 아직 Goal을 보낸 것은 아니다.

```python
self.goal_handle = None
self.finished = False
self.cancel_after = cancel_after
self.cancel_sent = False
self.start_time = None
```

- `goal_handle`: Goal 수락 응답을 받은 다음에 저장할 클라이언트 측 Goal Handle이다. 요청 전에는 `None`이다.
- `finished`: 프로그램의 `spin_once()` 루프를 종료할지 나타낸다. 결과를 받거나 거부되면 `True`로 변경한다.
- `cancel_after`: 자동 취소 요청까지 걸리는 시간(초)이다. `0` 또는 음수면 현 조건식상 자동 취소하지 않는다.
- `cancel_sent`: 여러 Feedback에서 중복 취소 요청을 보내지 않도록 하는 플래그다.
- `start_time`: `send_goal` 시작 전에는 없으며, 실제 Goal 비동기 전송 직전에 기준 시간을 저장한다. 이때부터 시간 계산을 시작한다는 점에 주의한다.

### 4.2 `send_goal()`: 사용자 입력을 Goal 메시지로 변환

```python
def send_goal(self, x, y):
    goal_msg = MoveToGoal.Goal()
    goal_msg.target_x = float(x)
    goal_msg.target_y = float(y)
```

- `send_goal`은 클래스 메서드이며 `x`, `y`는 터미널에서 해석한 실수 인자다.
- `MoveToGoal.Goal()`은 새로운 Goal 메시지 객체를 만든다. `float(x)`는 Python 내장 형변환 함수다. `argparse`에서 이미 `float`로 파싱했으므로 이 변환은 중복될 수 있지만 명시적인 형태를 유지한다.
- `goal_msg.target_x`는 Goal 메시지 필드에 값을 대입한다. 필드 이름은 `.action` 정의와 정확히 같아야 한다.

```python
self.get_logger().info('Waiting for Action Server...')
self.action_client.wait_for_server()
```

- 로그는 실제 서버 연결 여부와 무관하게 먼저 찍는다.
- `wait_for_server()`는 사용 가능한 같은 이름·타입의 Action Server를 찾을 때까지 대기하는 동기 블로킹 호출이다. 이 코드에는 별도 timeout 인자를 지정하지 않았으므로 서버가 없으면 계속 기다릴 수 있다.
- 이전에 클라이언트 파일이 비어 있었을 때는 이 로그조차 나오지 않았다. 이 현상은 ROS 통신 이상이 아니라 실행할 Python 코드가 없었던 문제였다.

```python
self.start_time = time.monotonic()
self.send_goal_future = self.action_client.send_goal_async(
    goal_msg,
    feedback_callback=self.feedback_callback
)
```

- `send_goal_async`는 Goal을 **비동기 전송**하며 완료 여부를 나타내는 `Future` 객체를 반환한다. 즉 이 함수의 반환값은 수락 여부가 아니라 미래에 완료될 작업을 가리킨다.
- `feedback_callback`에 전달한 것은 메서드 참조다. 서버가 중간 피드백을 발행하고 클라이언트의 Executor가 처리하면 호출된다.
- 비동기 전송은 즉시 도착 성공을 의미하지 않는다. 서버가 Goal을 수락했는지 확인하는 별도 Callback이 필요하다.

```python
self.send_goal_future.add_done_callback(
    self.goal_response_callback
)
```

- `Future.add_done_callback()`은 Future가 완료되었을 때 실행할 함수를 등록한다. 인자는 완료된 Future 객체로 전달된다.
- 반환 Future를 속성으로 저장하는 이유는 후속 관찰·접근을 가능하게 하기 위함이다. 실제 수락 응답 확인은 아래 메서드에서 수행한다.

### 4.3 `goal_response_callback()`: 수락 여부 처리

```python
def goal_response_callback(self, future):
    self.goal_handle = future.result()
```

- 여기서 `future.result()`는 Goal 요청의 **수락/거부 응답 핸들**을 가져온다. 최종 이동 Result와는 다르다.
- `self.goal_handle`은 수락 여부를 알려주는 `.accepted` 및 결과/취소 요청 메서드를 제공한다.

```python
if not self.goal_handle.accepted:
    self.get_logger().warn('Goal rejected.')
    self.finished = True
    return
```

- 수락되지 않으면 경고 로그를 출력하고 `finished=True`로 설정한다.
- `return`을 실행하므로 아래의 `get_result_async()`는 호출하지 않는다. 결과 요청을 기다릴 실제 Goal이 없기 때문이다.

```python
self.get_logger().info('Goal accepted.')
self.result_future = self.goal_handle.get_result_async()
self.result_future.add_done_callback(self.result_callback)
```

- Goal이 승인되면 성공적으로 접수되었다고 로깅한다. 이것은 최종 목표 달성 상태와 다르다.
- `get_result_async()`는 Goal이 끝날 때까지 대기할 결과 Future를 만든다. 이 요청은 별도 결과 Callback을 등록한 뒤 기다리는 비동기 방식이다.
- 결과를 바로 출력하려고 `get_result_async().result()`를 무리하게 기다리는 식으로 작성하면 Executor가 콜백을 처리하지 못해 교착 문제를 일으킬 수 있다.

### 4.4 `feedback_callback()`: 중간 피드백 읽기

```python
def feedback_callback(self, feedback_msg):
    feedback = feedback_msg.feedback
```

- Action Client의 피드백 콜백 인자는 `Feedback` 자체가 아니라 피드백을 감싼 메시지 객체다.
- `.feedback` 속성을 꺼내야 `current_x`, `current_y`, `distance_remaining`에 접근할 수 있다.

```python
self.get_logger().info(
    f'Position: ({feedback.current_x:.2f}, '
    f'{feedback.current_y:.2f}) | '
    f'Distance: {feedback.distance_remaining:.2f}'
)
```

- 여러 개의 f-string 리터럴을 괄호 안에 나란히 적으면 Python이 하나의 문자열로 연결한다. `:.2f`는 보여주는 자릿수만 바꾸고 실제 Feedback 필드 값을 변경하지 않는다.
- 실제 로그에서 `Position: (5.54, 5.54) | Distance: 3.47`로 시작해 마지막 `Distance: 0.14`까지 관측되었다.
- 중간에 같은 좌표가 여러 번 표시되거나 거리가 일시적으로 증가한 것은 실제 로그에서 확인된 현상이다. 시스템 스케줄링이나 선회 등 여러 요소가 관여할 수 있으며, 로그만으로 원인을 하나로 확정하지는 않는다.

### 4.5 Feedback을 이용한 자동 취소 조건

```python
if (
    self.cancel_after > 0
    and not self.cancel_sent
    and self.goal_handle is not None
    and time.monotonic() - self.start_time
    >= self.cancel_after
):
```

- 네 가지 조건이 **모두 참**이어야 아래 취소 코드가 실행된다.
- ① 취소 옵션이 0보다 커야 한다. ② 이전에 이미 취소 요청을 보내지 않았어야 한다. ③ 승인된 Goal 핸들이 존재해야 한다. ④ Goal 전송 직전에 기록한 시각으로부터 지정 시간 이상 흘렀어야 한다.
- 조건이 `feedback_callback` 안에 있기 때문에 시간이 정확히 3초가 되는 순간 실행되는 타이머가 아니다. **3초 이상 지난 후 들어온 첫 Feedback에서** 취소를 요청한다.

```python
self.cancel_sent = True
self.get_logger().info('Sending cancel request...')
cancel_future = self.goal_handle.cancel_goal_async()
cancel_future.add_done_callback(self.cancel_response_callback)
```

- `cancel_sent=True`가 중복 전송을 막는다.
- `cancel_goal_async()`는 취소 요청을 비동기 전송하고 Future를 반환한다. 요청 시점에는 아직 서버가 수락했는지 모른다.
- 로컬 변수 `cancel_future`는 해당 Callback 실행 범위에서 Future를 참조한다. 완료되면 등록된 `cancel_response_callback`이 호출된다.

### 4.6 취소 응답과 최종 Result는 다르다

```python
def cancel_response_callback(self, future):
    response = future.result()

    if response.goals_canceling:
        self.get_logger().info('Cancel accepted.')
    else:
        self.get_logger().warn('Cancel not accepted.')
```

- `future.result()`는 취소 요청 응답 메시지를 꺼낸다.
- `response.goals_canceling`은 취소 처리 대상으로 전환된 Goal의 목록이다. 비어 있지 않으면 Python에서 참(True)으로 평가된다.
- `Cancel accepted.`는 *서버가 취소 요청을 접수했다*는 의미다. 최종적으로 작업이 취소 완료되었는지는 **Result의 `STATUS_CANCELED`**로 별도로 확인한다.
- 실제 실습에서는 `Cancel accepted.`와 `Goal canceled.`가 모두 출력되었다.

### 4.7 최종 결과와 Action 상태

```python
def result_callback(self, future):
    response = future.result()
    result = response.result
    status = response.status
```

- 여기에서 Future의 결과는 Goal 처리 완료 후 반환되는 **최종 결과 응답**이다.
- `response.result`는 `MoveToGoal.Result` 메시지다. 이 안에는 사용자 정의 `success`, `final_x`, `final_y`가 있다.
- `response.status`는 ROS 2 Action이 제공하는 최종 상태 코드다. `result.success`와 별개로 관리되는 값이다.

```python
self.get_logger().info(
    f'Final position: '
    f'({result.final_x:.2f}, {result.final_y:.2f})'
)
```

- 최종적으로 서버가 보고한 마지막 관측 좌표를 출력한다. Turtlesim 내부의 완벽한 정지 시각을 보증하는 값이 아니라 마지막 Pose 기반 결과다.

```python
if status == GoalStatus.STATUS_SUCCEEDED:
    self.get_logger().info('Goal succeeded.')
elif status == GoalStatus.STATUS_CANCELED:
    self.get_logger().info('Goal canceled.')
elif status == GoalStatus.STATUS_ABORTED:
    self.get_logger().warn('Goal aborted.')
else:
    self.get_logger().warn(f'Goal status: {status}')

self.finished = True
```

- `if`/`elif`/`else`는 여러 경우 중 **첫 번째로 만족한 한 분기만 실행**한다.
- `==`는 동등 비교 연산자이고 `=`는 대입 연산자다. 두 기호를 혼동하면 안 된다.
- 성공·취소·중단 외 상태는 숫자 코드로 출력한다. 아래의 `finished=True`는 어떤 분기가 실행되든 결과 처리 후 루프를 끝내게 한다.
- 실제로 사용자가 확인한 로그는 `Goal succeeded.` 및 `Goal canceled.` 두 가지다. `Goal aborted.`는 실행 출력이 확인되지 않았다.

### 4.8 `argparse`를 이용한 CLI 인자

```python
def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('x', type=float)
    parser.add_argument('y', type=float)
```

- `ArgumentParser()`는 터미널 인자를 해석하는 파서 객체를 만든다.
- `'x'`, `'y'`처럼 `--` 없이 선언하면 **필수 위치 인자(positional argument)**가 된다. `type=float`가 붙었으므로 파서는 입력 문자열을 실수로 변환한다.
- 예: `python3 move_client.py 8.0 8.0` → `x=8.0`, `y=8.0`. 잘못된 문자열이면 `argparse`가 사용법과 오류를 표시하고 실행을 끝낸다.

```python
parser.add_argument(
    '--cancel-after',
    type=float,
    default=0.0
)
parsed_args = parser.parse_args()
```

- `--cancel-after`는 선택 인자다. 사용자 지정값이 없으면 기본값 `0.0`을 사용한다.
- `parse_args()`는 실행 시 주어진 CLI 인자를 읽어 Namespace 객체를 만든다. `parsed_args.x`, `parsed_args.y`, `parsed_args.cancel_after`로 접근한다.
- 하이픈이 있는 옵션 이름은 파싱 결과 속성에서 밑줄(`cancel_after`)로 바뀐다.

### 4.9 ROS 초기화, 노드 생성, `spin_once`

```python
rclpy.init(args=args)
node = TurtleMoveClient(cancel_after=parsed_args.cancel_after)
```

- 서버와 마찬가지로 노드 생성 전에 `rclpy.init()`이 필요하다.
- 인스턴스를 만들며 `cancel_after` 값을 생성자에 전달한다. 좌표는 이 시점이 아니라 아래 `send_goal()` 호출 시 전달된다.

```python
try:
    node.send_goal(parsed_args.x, parsed_args.y)

    while rclpy.ok() and not node.finished:
        rclpy.spin_once(node, timeout_sec=0.1)
```

- `send_goal()`을 호출하여 비동기 목표 전송을 시작한다. `wait_for_server()`는 이 호출 안에서 블로킹한다.
- `rclpy.spin_once(node, timeout_sec=0.1)`는 최대 약 0.1초 동안 준비된 콜백 작업 하나를 처리하도록 ROS 2에 기회를 준다. 이것을 반복해 Goal 응답, Feedback, 취소 응답, 최종 Result Callback이 실행된다.
- `node.finished`가 `True`가 되면 루프를 종료한다. 서버의 `executor.spin()`과 달리 이 클라이언트는 **목표 하나의 종료 후 프로그램을 자동 종료**하도록 설계했다.

```python
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

- `Ctrl+C`는 KeyboardInterrupt로 처리한다. `finally`는 노드와 ROS 실행 컨텍스트를 정리한다.
- 주의: 클라이언트를 `Ctrl+C`로 종료하는 것이 서버의 Goal을 자동 취소한다는 뜻은 아니다. 서버 측 작업을 확실히 취소하려면 Action Cancel 요청을 별도로 보내야 한다.

```python
if __name__ == '__main__':
    main()
```

- 이전에 `move_client.py` 파일이 비어 있었을 때 명령이 로그 없이 즉시 종료된 이유를 여기서 이해할 수 있다. 파일 안에 실행 코드가 없으면 Python은 정의나 콜백을 실행할 일이 없다.
- 이 부분의 `main()` 호출이 있어야 `python3 move_client.py ...` 명령에서 실질적인 Goal 전송이 시작된다.

## 5. `MoveToGoal.action` 전체 내용 및 필드 분석

```text
float32 target_x
float32 target_y
---
bool success
float32 final_x
float32 final_y
---
float32 current_x
float32 current_y
float32 distance_remaining
```

- 첫 번째 영역인 **Goal**은 `target_x`, `target_y`를 가진다. 사용자가 요청한 목표 지점이며 Server의 `goal_callback`/`execute_callback`에서 읽는다.
- 첫 번째 `---` 다음 영역은 **Result**다. `success`는 사용자 정의 성공 여부, `final_x`, `final_y`는 마지막으로 관측한 위치다. Action 시스템이 제공하는 `status`와 중복이 아니라 역할이 다르다.
- 두 번째 `---` 다음 영역은 **Feedback**이다. `current_x`, `current_y`, `distance_remaining`을 담고 실행 중 여러 차례 발행된다.
- `float32`는 32비트 실수형, `bool`은 논리형이다. Python 측에서는 생성된 메시지 타입에 맞는 필드 대입이 요구된다.
- `.action` 파일 자체는 Python으로 실행되지 않는다. ROSIDL이 빌드할 때 이 정의를 읽고 Python 인터페이스 등을 생성한다.

## 6. `CMakeLists.txt` 전체 내용과 각 줄

```cmake
cmake_minimum_required(VERSION 3.8)
project(turtle_move_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/MoveToGoal.action"
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
```

1. `cmake_minimum_required(VERSION 3.8)`: 빌드에 필요한 최소 CMake 버전을 선언한다.
2. `project(turtle_move_interfaces)`: CMake 프로젝트 이름을 정의한다. `${PROJECT_NAME}`는 이후 이 이름으로 확장되는 CMake 변수 참조이다.
3. `find_package(ament_cmake REQUIRED)`: ROS 2의 CMake 빌드 도구를 찾는다. `REQUIRED`이므로 없으면 구성 단계에서 실패한다.
4. `find_package(rosidl_default_generators REQUIRED)`: `.action`/`.msg`/`.srv`에서 언어별 인터페이스를 생성할 도구를 찾는다.
5. `rosidl_generate_interfaces(${PROJECT_NAME} "action/MoveToGoal.action")`: 사용자 정의 Action 파일을 생성 대상으로 지정한다. 이 구문이 실습 07의 인터페이스 빌드 핵심이다.
6. `ament_export_dependencies(rosidl_default_runtime)`: 이 패키지를 사용하는 다른 패키지에 런타임 의존성을 알리는 설정이다.
7. `ament_package()`: ROS 2 ament 패키지 메타데이터/설치 관련 처리의 마무리다.

## 7. `package.xml` 내용 및 의존 관계

> 아래는 앞서 대화에서 제시한 예시 내용이다. XML 오류를 수정한 실제 로컬 파일의 최종 본문은 직접 확인하지 못했으므로, 로컬에서 수정한 이메일·공백 등 세부 내용과 다를 수 있다.

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>turtle_move_interfaces</name>
  <version>0.0.1</version>
  <description>Custom action interface for Turtlesim movement</description>
  <maintainer email="kmw@example.com">kmw</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>rosidl_default_generators</buildtool_depend>

  <depend>action_msgs</depend>
  <exec_depend>rosidl_default_runtime</exec_depend>

  <member_of_group>rosidl_interface_packages</member_of_group>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

- `<?xml version="1.0"?>`은 XML 선언이며 **파일의 맨 앞**에 있어야 한다. 실제 빌드 실패 원인은 선언보다 앞에 빈 줄 또는 텍스트가 있어 `line 2, column 0` 오류가 난 것이었다.
- `<package format="3">`는 ROS 패키지 매니페스트 형식을 나타낸다. 각 XML 요소는 열고 닫는 태그로 쌍을 이룬다.
- `<name>`과 CMake의 `project(...)` 이름은 여기서 `turtle_move_interfaces`로 일치한다.
- `<buildtool_depend>ament_cmake</buildtool_depend>`는 빌드 시스템 의존성을, `<buildtool_depend>rosidl_default_generators</buildtool_depend>`는 빌드 시 인터페이스 코드 생성 의존성을 선언한다.
- `<depend>action_msgs</depend>`는 Action에서 쓰는 공통 메시지 의존성이다.
- `<exec_depend>rosidl_default_runtime</exec_depend>`는 생성 인터페이스를 사용하는 런타임 의존성이다.
- `<member_of_group>rosidl_interface_packages</member_of_group>`는 인터페이스 패키지 그룹 소속임을 나타낸다.
- `<export><build_type>ament_cmake</build_type></export>`는 ROS 2가 사용할 빌드 유형을 공개한다.
- `kmw@example.com`은 제공된 예시 주소이며 실제 사용하는 이메일이 아님을 유의한다.

## 8. 두 프로세스와 Turtlesim의 실제 실행 순서

```text
[Terminal 1: turtlesim]
  turtlesim_node
      ├─ publishes /turtle1/pose --------------------------┐
      └─ subscribes /turtle1/cmd_vel <-------------------┐ |
                                                         | |
[Terminal 2: server]                                     | |
  rclpy.init()                                            | |
  TurtleMoveServer()                                      | |
      ├─ create_subscription(/turtle1/pose) <-------------|-┘
      ├─ create_publisher(/turtle1/cmd_vel) --------------┘
      └─ ActionServer(/move_to_goal)
  MultiThreadedExecutor.spin()

[Terminal 3: client]
  rclpy.init() → TurtleMoveClient() → send_goal(8.0, 8.0)
      ├─ wait_for_server()
      ├─ send_goal_async() → Server.goal_callback()
      │                       ├─ REJECT: Client.finished = True
      │                       └─ ACCEPT: Server.execute_callback()
      │                             ├─ read latest Pose
      │                             ├─ calculate distance/heading
      │                             ├─ publish Twist
      │                             ├─ publish Feedback ------> feedback_callback()
      │                             └─ succeed/canceled/abort → Result
      └─ get_result_async() ------------------------------> result_callback()
                                                              └─ finished = True
```

이 다이어그램의 핵심은 다음과 같다.

- Turtlesim, Action Server, Action Client는 별도의 프로세스다. 그 사이에서 Python 메서드를 직접 호출하는 것이 아니라 ROS 2 통신 미들웨어가 메시지와 Goal 요청을 전달한다.
- Pose와 Twist는 계속 흐르는 Topic 데이터이며 Action Goal을 처리하는 데 필요한 내부 정보다.
- Client는 결과를 얻기 위해 Server의 실행 루프가 끝날 때까지 Python 코드를 동기적으로 멈춰 두는 대신 Future와 Callback을 사용한다.
- Server는 장시간 실행 Callback과 위치 수신 Callback이 동시에 처리될 수 있도록 `ReentrantCallbackGroup`과 `MultiThreadedExecutor`를 사용한다.
- `result_callback()`이 실행되어 `finished=True`가 되면 Client의 `spin_once()` 반복이 끝나고 종료된다. Server는 다음 Goal을 위해 계속 실행된다.

## 9. 실제 로그와 코드 동작 연결

### 9.1 목표 `(8, 8)` 도착 — 실행으로 확인됨

```text
Goal accepted.
Position: (5.54, 5.54) | Distance: 3.47
...
Position: (7.97, 7.87) | Distance: 0.14
Final position: (7.99, 7.86)
Goal succeeded.
```

- `Goal accepted.`: `goal_callback()`의 `GoalResponse.ACCEPT`와 클라이언트의 `goal_response_callback()`이 대응한다.
- 여러 `Position` 로그: 서버가 `publish_feedback()`을 여러 차례 호출했고 클라이언트가 `feedback_callback()`에서 출력했다.
- `Distance: 0.14`: 서버의 `if distance < 0.15` 조건을 만족하는 피드백이다.
- `Goal succeeded.`: 서버에서 `goal_handle.succeed()`를 호출하고, 클라이언트가 `response.status`를 `STATUS_SUCCEEDED`로 판별한 결과다.
- 최종 위치 `(7.99, 7.86)`은 정확한 목표 `(8.0, 8.0)`과 다르지만 **허용 오차 내 도착**이므로 성공 판정과 일치한다.

### 9.2 약 3초 뒤 Goal 취소 — 실행으로 확인됨

```text
Position: (7.99, 7.86) | Distance: 8.38
...
Position: (6.93, 6.99) | Distance: 7.02
Sending cancel request...
Cancel accepted.
Final position: (6.72, 6.80)
Goal canceled.
```

- `Sending cancel request...`: Feedback 콜백의 조건을 만족해 `cancel_goal_async()`를 호출했다.
- `Cancel accepted.`: 서버가 `CancelResponse.ACCEPT`를 반환하고 클라이언트에서 `response.goals_canceling`을 확인했다.
- `Goal canceled.`: 그다음 서버 실행 루프가 취소 플래그를 확인하고 `goal_handle.canceled()`로 종료시켰다.
- 요청을 보낸 위치와 최종 위치가 다른 이유는 취소 요청·수락·제어 루프의 취소 확인·정지 명령 발행에 시간이 걸리기 때문이다.

### 9.3 잘못된 좌표 거부 — 예상이며 미검증

```bash
python3 -u move_client.py 15.0 15.0
```

- 서버의 `goal_callback()`은 `0.5 <= x <= 10.5`, `0.5 <= y <= 10.5`를 검사하므로 이 Goal은 거부되는 것이 예상 결과다.
- 클라이언트는 `goal_handle.accepted`가 거짓이면 `Goal rejected.`를 출력한 뒤 종료하도록 작성되어 있다.
- **이 테스트의 터미널 결과는 아직 전달되지 않았으므로 실행 완료라고 기록하지 않는다.**

## 10. 코드 일부만 변경하며 이해하는 실험

아래 실험은 실제로 실행했다고 확인된 내용이 아니라 **예상 결과와 검증 방법**이다. 원본 수치를 기록한 뒤 바꿨다가 되돌리면 된다. 이 예제에서는 Python 코드만 바꾸므로 인터페이스 재빌드는 필요 없다.

### 실험 A — 도착 허용 오차 바꾸기

원본(`move_server.py`):

```python
if distance < 0.15:
```

변경:

```python
if distance < 0.05:
```

예상: 목표에 더 가까워져야 성공 처리된다. 다만 오차가 작아질수록 제어기 특성상 성공까지 시간이 늘거나 진동·타임아웃 가능성이 증가할 수 있다. 확인: 같은 시작 위치에서 마지막 Feedback `distance_remaining`과 최종 Result를 비교한다.

### 실험 B — 최대 선속도 제한 바꾸기

원본:

```python
cmd.linear.x = min(1.5, distance)
```

변경:

```python
cmd.linear.x = min(0.7, distance)
```

예상: 먼 거리에서의 최대 전진 속도 명령이 낮아져 이동 시간이 늘어날 수 있다. 정확한 소요 시간은 실제로 측정해야 한다. 확인: Client 실행 전후 시각 및 Turtlesim 이동을 관찰한다.

### 실험 C — 회전 우선 임계값 바꾸기

원본:

```python
if abs(angle_error) > 0.35:
```

변경:

```python
if abs(angle_error) > 0.15:
```

예상: 작은 방향 오차에도 제자리 회전이 더 자주 적용되어 경로가 바뀔 수 있다. 확인: Turtlesim 경로와 `ros2 topic echo /turtle1/cmd_vel`을 함께 관찰한다.

### 실험 D — 자동 취소 시점 바꾸기

원본 실행 명령:

```bash
python3 -u move_client.py 2.0 2.0 --cancel-after 3
```

변경:

```bash
python3 -u move_client.py 2.0 2.0 --cancel-after 1
```

예상: 1초가 지난 뒤 처음 도착하는 Feedback에서 취소가 요청된다. 초 단위의 정확한 타이머가 아니므로 로그 시간을 함께 기록한다. Python 파일을 수정할 필요가 없다.

## 11. 빌드·실행 시 혼동하기 쉬운 부분

| 상황 | 필요한 조치 | 이유 |
| --- | --- | --- |
| `.action` 정의 수정 | `colcon build --symlink-install` 후 `source install/setup.bash` | 생성 메시지 타입을 갱신해야 함 |
| `move_server.py` 제어 값 수정 | 서버 프로세스 재시작 | 직접 실행하는 Python 파일이므로 재빌드 불필요 |
| `move_client.py` 로그 수정 | 클라이언트 다시 실행 | 직접 실행하는 Python 파일이므로 재빌드 불필요 |
| 새 터미널에서 Custom Action Import 실패 | ROS 2 및 `install/setup.bash` 다시 source | 환경 변수는 현재 셸 단위로 설정됨 |
| `package.xml` XML 선언 오류 | 첫 줄의 XML 선언 위치 수정 후 재빌드 | 빌드 전 패키지 메타데이터 파싱 단계에서 실패 |
| Client 실행 후 아무 로그 없이 종료 | 실제 파일 크기 및 `main()` 호출 확인 | 이번 실습에서 실제로 발생한 원인: 빈 `move_client.py` |

### 재현용 명령어

```bash
cd ~/ros2_practice/07_turtlesim_action
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
colcon build --symlink-install
source install/setup.bash
ros2 interface show turtle_move_interfaces/action/MoveToGoal
python3 -c "from turtle_move_interfaces.action import MoveToGoal; print('Action import successful')"
```

인터페이스를 빌드한 뒤에는 세 터미널에서 각각 `turtlesim_node`, `move_server.py`, `move_client.py`를 실행한다. 자세한 터미널 분리는 `README.md`의 **Run the Complete System**에 기록했다.
