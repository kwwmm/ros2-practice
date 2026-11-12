# Practice 06 — ROS2 Action Server & Client: 코드 상세 분석

## 1. `action_server.py` — 전체 Python 코드

```python
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from action_tutorials_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')

        self.action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )

        self.get_logger().info('Action Server started.')

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received.')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        order = goal_handle.request.order

        result = Fibonacci.Result()

        if order <= 0:
            result.sequence = []
            goal_handle.succeed()
            return result

        if order == 1:
            result.sequence = [0]
            goal_handle.succeed()
            return result

        for i in range(2, order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.sequence = feedback_msg.partial_sequence
                self.get_logger().info('Goal canceled.')
                return result

            next_number = (
                feedback_msg.partial_sequence[i - 1]
                + feedback_msg.partial_sequence[i - 2]
            )

            feedback_msg.partial_sequence.append(next_number)

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'Feedback: {feedback_msg.partial_sequence}'
            )

            time.sleep(1.0)

        goal_handle.succeed()

        result.sequence = feedback_msg.partial_sequence

        self.get_logger().info('Goal succeeded.')

        return result


def main(args=None):
    rclpy.init(args=args)

    node = FibonacciActionServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

### 1.1 `import`와 의존성

```python
import time
```

- Python 표준 라이브러리인 `time` **모듈**을 가져온다. 패키지 설치가 필요하지 않다.
- 아래의 `time.sleep(1.0)`에서 실행 흐름을 **1초 동안 중지**하는 데 사용한다.
- `sleep()`은 비동기 대기가 아닌 **블로킹 호출**이다. 현재 `execute_callback()`을 수행 중인 스레드가 잠시 멈춘다. 다른 스레드까지 모두 멈추는 것은 아니다.

```python
import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
```

- `rclpy`: Python에서 ROS2 노드와 통신 기능을 사용하는 라이브러리다. `rclpy.init()`과 `rclpy.try_shutdown()` 등을 호출한다.
- `from ... import ...`: 모듈에서 특정 클래스나 이름만 현재 파일의 이름 공간으로 가져오는 Python 문법이다.
- `ActionServer`: Action 목표 수신·실행·피드백·결과 응답을 관리하는 서버 객체를 만드는 클래스다.
- `CancelResponse`: 취소 요청을 받아들일지 거절할지 나타내는 열거형 값들을 제공한다. 이 코드에서는 `CancelResponse.ACCEPT`를 반환한다.
- `ReentrantCallbackGroup`: 같은 그룹에 속한 콜백들이 서로 겹쳐 실행되는 것을 허용한다. 실제 동시 실행 여부는 Executor의 스레드 수 등에도 좌우된다.
- `MultiThreadedExecutor`: 여러 스레드를 사용하여 준비된 콜백을 처리하는 실행기다.
- `Node`: 사용자 노드를 만드는 기반 클래스다. 상속받은 노드에서는 로거, 통신 객체 등 ROS2 기능을 사용할 수 있다.

```python
from action_tutorials_interfaces.action import Fibonacci
```

- ROS2에서 제공하는 `Fibonacci` **Action 인터페이스 클래스**를 가져온다.
- `Fibonacci.Goal`, `Fibonacci.Feedback`, `Fibonacci.Result` 세 메시지 종류를 사용한다.
- 이 Action의 정의는 다음과 같다. `---`는 필드 묶음을 나누는 구분자이며, 순서는 Goal / Result / Feedback이다.

```text
int32 order
---
int32[] sequence
---
int32[] partial_sequence
```

- `order`: 목표 수열 길이를 나타내는 정수다.
- `sequence`: 최종 결과 또는 취소 시점의 부분 수열이다.
- `partial_sequence`: 실행 도중 전송하는 부분 수열이다.
- `int32`는 32비트 부호 있는 정수다. 수열 항이 너무 커지면 메시지 변환 과정에서 오류가 발생할 수 있으므로 작은 `order`를 사용한다.

### 1.2 클래스, 상속, 생성자

```python
class FibonacciActionServer(Node):
```

- `class`: 새로운 Python 클래스 정의를 시작한다.
- `FibonacciActionServer`: 이 실습에서 만든 클래스 이름이다.
- `(Node)`: `Node` 클래스를 **상속**한다는 뜻이다. 따라서 이 클래스 인스턴스를 하나 만들면 ROS2 노드처럼 사용할 수 있다.
- 마지막의 `:`와 다음 줄의 들여쓰기는 클래스 본문이 시작됨을 나타낸다.

```python
    def __init__(self):
        super().__init__('fibonacci_action_server')
```

- `def`: 함수를 정의하는 키워드다. 클래스 내부의 함수는 보통 **메서드**라고 부른다.
- `__init__`: 객체가 생성될 때 호출되는 **초기화 메서드**다.
- `self`: 현재 만들어지고 있는 `FibonacciActionServer` 인스턴스를 가리킨다. Python이 인스턴스 메서드 호출 시 자동으로 전달한다.
- `super()`: 부모 클래스인 `Node`의 메서드를 사용할 수 있게 한다.
- `super().__init__(...)`: `Node` 생성자를 실행하여 ROS2 노드의 기반 기능을 초기화한다.
- `'fibonacci_action_server'`: ROS 그래프에 나타날 **노드 이름**이다. Action 이름인 `'fibonacci'`와는 다르다.
- 부모 생성자 호출을 빼면 노드가 정상 초기화되지 않아 이후 Action Server 생성이나 로거 사용이 실패할 수 있다.

### 1.3 `ActionServer()` 생성과 콜백 등록

```python
        self.action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )
```

- 오른쪽의 `ActionServer(...)`는 **생성자 호출**이며, Action Server 객체를 반환한다.
- `self.action_server = ...`: 생성한 객체를 현재 노드의 **인스턴스 속성**에 보관한다. `self.`를 사용하므로 생성자 밖에서도 같은 객체에 접근할 수 있다.
- 첫 번째 인자 `self`: 이 Action Server를 소유하는 ROS2 노드 객체다.
- 두 번째 인자 `Fibonacci`: Goal/Feedback/Result 타입을 정의하는 Action 인터페이스다. Client의 인터페이스와 일치해야 한다.
- 세 번째 인자 `'fibonacci'`: **Action 이름**이다. 전체 이름은 일반적인 기본 네임스페이스에서 `/fibonacci`로 보인다.
- `execute_callback=self.execute_callback`: **Goal 실행 시 사용할 메서드 참조**를 전달한다. 여기서 괄호를 붙이지 않았으므로 서버 생성 순간에 `execute_callback()`을 직접 실행하는 것이 아니다.
- `cancel_callback=self.cancel_callback`: Client가 취소를 요청했을 때 처리할 메서드 참조다.
- `callback_group=ReentrantCallbackGroup()`: 해당 Action Server의 콜백을 재진입 허용 그룹에 배정한다. `MultiThreadedExecutor(num_threads=2)`와 조합하여 실행 콜백이 `sleep()` 중일 때도 취소 콜백을 처리할 수 있게 한다.
- `goal_callback`은 따로 지정하지 않았다. 이 예제에서는 기본 Goal 수락 동작을 사용한다.
- 콜백으로 전달되는 `goal_handle`은 **현재 목표를 다루는 서버 측 핸들 객체**다. 모든 Goal이 공유하는 단순 전역 변수가 아니다.

```python
        self.get_logger().info('Action Server started.')
```

- `self.get_logger()`는 ROS2 로거 객체를 얻는다.
- `.info(...)`는 정보 수준의 로그를 출력한다.
- 서버를 생성한 뒤 한 번 실행된다. **서버 시작 로그가 출력되었다고 Client의 Goal 처리가 이미 끝난 것은 아니다.**

### 1.4 취소 요청 콜백

```python
    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received.')
        return CancelResponse.ACCEPT
```

- `cancel_callback`은 Client가 Action의 **취소 요청**을 보낼 때 실행된다.
- `goal_handle`은 해당 취소 대상 Goal에 대한 서버 측 핸들이다. 이 코드에서는 인자로 받지만 내부에서 참조하지 않는다.
- `return`은 호출한 ROS2 Action 처리 코드로 값을 돌려주는 Python 문법이다.
- `CancelResponse.ACCEPT`는 **취소 요청을 수락**한다는 뜻이다. 이 값만 반환한다고 실행 중인 `execute_callback()`이 즉시 중지되는 것은 아니다.
- 실제 중단은 아래 반복문의 `goal_handle.is_cancel_requested` 검사와 `goal_handle.canceled()` 호출로 이루어진다.
- 따라서 취소 요청 수락과 목표 상태가 최종적으로 `CANCELED`가 되는 순간은 구별해야 한다.

### 1.5 Goal 실행 콜백: 초기화와 입력 읽기

```python
    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
```

- 서버가 Goal을 실행하기 시작할 때 `execute_callback()`이 호출된다.
- `goal_handle`을 통해 요청의 내용, 취소 상태, 피드백 발행, 성공/취소 처리를 수행한다.
- `execute_callback()`은 **최종적으로 `Fibonacci.Result` 객체를 반환**해야 한다.

```python
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]
```

- `Fibonacci.Feedback()`은 피드백 메시지 객체를 만든다.
- `feedback_msg`: 이 객체를 가리키는 지역 변수다. 함수가 실행될 때마다 별도로 만들어진다.
- `.partial_sequence`: 인터페이스에 정의된 `int32[]` 필드다.
- `[0, 1]`: 정수 두 개가 들어 있는 Python **리스트(list)**다. `[]`는 리스트 리터럴 문법이다.
- 이후 `append()`로 리스트를 변경하면서 피보나치 수열을 만든다.
- 이 시점에는 피드백을 전송하지 않았다. 실제 발행은 `publish_feedback()`을 호출하는 부분에서 이루어진다.

```python
        order = goal_handle.request.order
        result = Fibonacci.Result()
```

- `goal_handle.request`는 서버가 받은 Goal 요청 메시지다.
- `.order` 필드 값을 읽어 지역 변수 `order`에 저장한다.
- `result`는 최종 응답으로 돌려줄 `Fibonacci.Result` 객체다.
- `result.sequence`는 나중에 채운다. `Result()`만 생성했다고 결과가 Client에 전송되는 것은 아니다.

### 1.6 `order` 예외 분기

```python
        if order <= 0:
            result.sequence = []
            goal_handle.succeed()
            return result
```

- `if`: 조건이 참일 때만 들여쓴 본문을 실행한다.
- `<=`: **작거나 같다**는 비교 연산자다.
- `order <= 0`이면 비어 있는 리스트 `[]`를 결과에 넣는다.
- `goal_handle.succeed()`는 Goal의 상태를 **성공(SUCCEEDED)** 으로 설정한다.
- `return result`는 함수 실행을 즉시 종료하고 Result 객체를 Action 처리 측에 반환한다. 따라서 아래 반복문은 실행되지 않는다.
- 이 코드는 0 이하의 길이를 **거부하지 않고 빈 수열로 성공 처리**하도록 설계되어 있다.

```python
        if order == 1:
            result.sequence = [0]
            goal_handle.succeed()
            return result
```

- `==`는 값의 **동등성 비교**이며, 값을 대입하는 `=`와 다르다.
- 길이가 1이면 `[0]`만 결과로 반환한다.
- 두 예외 분기에서는 `publish_feedback()`이 호출되지 않으므로 피드백 메시지가 나오지 않는다.
- 길이 2 역시 아래 반복문 `range(2, 2)`가 비어 있어 피드백 없이 `[0, 1]`을 반환한다.

### 1.7 반복문과 취소 상태 검사

```python
        for i in range(2, order):
```

- `for`: 순회하는 반복문이다.
- `range(2, order)`: 2부터 `order - 1`까지 정수를 순서대로 만든다. 끝값 `order`는 포함하지 않는다.
- `order=10`이면 `i` 값은 `2, 3, 4, 5, 6, 7, 8, 9`다. 따라서 8개의 새 항을 추가해 `[0, 1]`을 포함한 총 10개 항을 완성한다.
- `i`는 지금 계산하려는 수열 항의 **0부터 시작하는 인덱스**다.

```python
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.sequence = feedback_msg.partial_sequence
                self.get_logger().info('Goal canceled.')
                return result
```

- `goal_handle.is_cancel_requested`: 해당 목표에 대해 수락된 취소 요청이 있는지 확인하는 속성이다.
- 참이면 `goal_handle.canceled()`로 최종 Goal 상태를 **취소(CANCELED)** 로 바꾼다.
- 현재까지 만든 `partial_sequence`를 `result.sequence`에 담는다. 즉, 이 예제는 취소되어도 **부분 결과**를 반환한다.
- 로그를 남기고 `return`하므로 남은 계산은 하지 않는다.
- 취소 여부는 **매 반복의 시작**에서 확인한다. 아래의 `time.sleep(1.0)` 진행 중에는 이 줄을 다시 검사하지 않으므로 취소가 즉각 반영되지 않을 수 있다.

### 1.8 다음 피보나치 항 계산

```python
            next_number = (
                feedback_msg.partial_sequence[i - 1]
                + feedback_msg.partial_sequence[i - 2]
            )
```

- `=`는 오른쪽에서 계산한 값을 왼쪽 변수에 할당한다.
- `partial_sequence[i - 1]`: 바로 앞의 항을 가져오는 **인덱싱**이다.
- `partial_sequence[i - 2]`: 두 항 전의 값을 가져온다.
- `+`는 정수 덧셈 연산이다.
- 괄호 `(...)`로 여러 줄에 걸쳐 하나의 표현식을 작성할 수 있다. 이 괄호는 함수 호출이 아니라 **표현식 그룹화**다.
- 예를 들어 `i=2`일 때 `partial_sequence[1] + partial_sequence[0]`은 `1 + 0 = 1`이다.
- `i=3`일 때는 `partial_sequence[2] + partial_sequence[1] = 1 + 1 = 2`가 된다.

```python
            feedback_msg.partial_sequence.append(next_number)
```

- `append(value)`는 리스트의 **맨 뒤에 원소 하나를 추가**하는 Python 리스트 메서드다.
- 기존 리스트 객체를 직접 변경한다. 새로운 리스트를 반환해 재할당하는 코드가 아니다.
- 예: `[0, 1]` → `[0, 1, 1]` → `[0, 1, 1, 2]`.

### 1.9 피드백 발행, 로그, 지연

```python
            goal_handle.publish_feedback(feedback_msg)
```

- `publish_feedback(...)`은 **현재 Goal에 대한 Feedback 메시지**를 Client 측으로 전달하도록 요청한다.
- 인자 `feedback_msg`의 메시지 타입은 `Fibonacci.Feedback`이다.
- 반복마다 한 번 호출되므로 `order=10`에서는 최대 8번의 피드백을 보낸다. 실제 네트워크 상황이나 취소 시점에 따라 수신한 피드백 수는 달라질 수 있다.
- ROS2 통신이므로 Client는 서버와 **별도 프로세스**에서도 해당 피드백을 받을 수 있다.

```python
            self.get_logger().info(
                f'Feedback: {feedback_msg.partial_sequence}'
            )
```

- `f'...'`는 **f-string**이다. `{...}` 안의 Python 표현식을 평가한 문자열로 만든다.
- 예를 들어 리스트가 `[0, 1, 1]`이면 `Feedback: [0, 1, 1]`이 출력된다.
- 이 로그는 **서버 터미널**에 출력된다. Client 터미널에 나타나는 Feedback 로그는 Client의 별도 콜백에서 작성한 것이다.

```python
            time.sleep(1.0)
```

- 현재 실행 스레드를 약 1초 동안 블로킹한다.
- `1.0`은 초 단위의 실수(float)다.
- 피보나치 계산에 본래 필요한 시간은 아니며, **장시간 작업처럼 Feedback과 취소 과정을 관찰하기 위한 실습용 지연**이다.
- 이 구간에서는 취소 요청이 승인되더라도 다음 반복문 시작까지 실행 콜백이 중단되지 않을 수 있다.
- **주의:** 마지막 반복에서도 `sleep()`이 실행되므로 마지막 Feedback 뒤 약 1초가 지난 다음 성공 처리한다.

### 1.10 정상 종료와 Result 반환

```python
        goal_handle.succeed()

        result.sequence = feedback_msg.partial_sequence

        self.get_logger().info('Goal succeeded.')

        return result
```

- 반복문을 중단 없이 끝내면 `succeed()`로 목표의 최종 상태를 **성공**으로 표시한다.
- 만들어 둔 리스트를 `result.sequence` 필드에 할당한다.
- 성공 로그를 출력하고 결과 객체를 반환한다.
- `goal_handle.succeed()`가 Result 객체 그 자체를 반환하는 것은 아니다. **상태 설정**과 **`return result`에 의한 결과 전달**은 역할이 다르다.
- `order=10`일 때 예상 결과는 `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`다.

### 1.11 `main()`과 노드 실행·종료

```python
def main(args=None):
    rclpy.init(args=args)
```

- `main`은 프로그램을 시작하는 일반 Python 함수다. 이름 자체가 ROS2 예약어는 아니다.
- `args=None`: 호출자가 인자를 전달하지 않으면 기본값으로 `None`을 사용한다. `None`은 Python에서 **값이 없음**을 나타내는 객체다.
- `rclpy.init(args=args)`: ROS2 Python 실행 환경(context)을 초기화한다. 노드 생성보다 먼저 호출해야 한다.

```python
    node = FibonacciActionServer()
```

- 클래스 이름 뒤에 `()`를 붙여 **객체(인스턴스)를 생성**한다.
- 내부에서 `__init__()`이 호출되고 ROS2 노드와 Action Server가 설정된다.
- `node`는 만든 인스턴스를 참조하는 지역 변수다.

```python
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
```

- `MultiThreadedExecutor(num_threads=2)`: 콜백 처리를 위해 **두 개의 작업 스레드**를 사용하는 Executor 객체를 만든다.
- `.add_node(node)`: 이 Executor가 처리할 노드를 등록한다. 노드의 Action 관련 콜백들이 Executor에 의해 실행될 수 있다.
- 이 코드에서 `ReentrantCallbackGroup()`과 함께 쓰는 이유는 Goal 실행 중 취소 요청을 처리하기 위함이다.
- 스레드가 둘이라고 해서 하나의 피보나치 반복문이 자동으로 병렬 계산되는 것은 아니다.

```python
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()
```

- `try`: 예외가 발생할 수 있는 코드를 실행한다.
- `executor.spin()`: ROS2 이벤트를 기다리면서 Goal 처리, 취소 요청 등의 콜백 실행을 계속 담당한다. 일반적으로 종료 요청이 올 때까지 반환하지 않는다.
- `except KeyboardInterrupt`: 터미널에서 `Ctrl+C`로 중단했을 때 발생할 수 있는 예외를 받는다.
- `pass`: 이 예외에 대해 추가 작업을 하지 않고 다음 구문으로 넘어간다.
- `finally`: 예외 유무와 관계없이 실행되는 정리 블록이다.
- `executor.shutdown()`: Executor의 작업 처리를 중지하고 관련 스레드를 정리한다.
- `node.destroy_node()`: ROS2 노드를 명시적으로 파괴한다.
- `rclpy.try_shutdown()`: ROS2 context가 아직 활성 상태인 경우 종료를 시도한다. 이미 종료된 상태에서 중복 종료 예외를 피하기 위해 사용한다.
- 주의: 처리 중인 Goal과 정리 시점이 겹치면 종료 상황에 따른 로그 차이가 날 수 있다.

```python
if __name__ == '__main__':
    main()
```

- Python이 파일을 **직접 실행**하면 특수 변수 `__name__`이 `'__main__'`이 된다.
- 따라서 `python3 action_server.py`로 실행하면 `main()`을 호출한다.
- 다른 파일에서 모듈로 import하면 자동으로 `main()`을 실행하지 않는다.
- 이런 조건문을 **메인 가드(main guard)** 라고 한다.

---

## 2. `action_client.py` — 전체 Python 코드

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from action_msgs.msg import GoalStatus
from action_tutorials_interfaces.action import Fibonacci


class FibonacciActionClient(Node):

    def __init__(self):
        super().__init__('fibonacci_action_client')

        self.action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci'
        )

        self.goal_handle = None
        self.feedback_count = 0
        self.cancel_after = 0
        self.cancel_sent = False

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self.get_logger().info('Waiting for Action Server...')

        self.action_client.wait_for_server()

        self.get_logger().info(f'Sending goal: {order}')

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
            self.get_logger().info('Goal rejected.')
            return

        self.get_logger().info('Goal accepted.')

        self.result_future = self.goal_handle.get_result_async()

        self.result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback

        self.feedback_count += 1

        self.get_logger().info(
            f'Feedback: {feedback.partial_sequence}'
        )

        if (
            self.cancel_after > 0
            and self.feedback_count >= self.cancel_after
            and not self.cancel_sent
            and self.goal_handle is not None
        ):
            self.cancel_sent = True

            self.get_logger().info('Requesting cancellation...')

            self.cancel_future = self.goal_handle.cancel_goal_async()

            self.cancel_future.add_done_callback(
                self.cancel_response_callback
            )

    def cancel_response_callback(self, future):
        response = future.result()

        if response.goals_canceling:
            self.get_logger().info('Cancel request accepted.')
        else:
            self.get_logger().info('Cancel request not accepted.')

    def result_callback(self, future):
        response = future.result()

        result = response.result
        status = response.status

        self.get_logger().info(f'Result: {result.sequence}')

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Goal succeeded.')

        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info('Goal canceled.')

        else:
            self.get_logger().info(f'Goal status: {status}')


def main(args=None):
    rclpy.init(args=args)

    node = FibonacciActionClient()

    try:
        node.send_goal(10)
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

### 2.1 Client의 import와 노드 클래스

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from action_tutorials_interfaces.action import Fibonacci
```

- `ActionClient`: Action Server에 Goal을 요청하고 피드백과 결과를 받는 Client 객체를 만드는 클래스다.
- `Node`: Client 또한 독립된 **ROS2 노드**이므로 상속한다.
- `GoalStatus`: Goal의 최종 실행 상태를 나타내는 상수들을 제공한다. 이 코드에서는 `STATUS_SUCCEEDED`와 `STATUS_CANCELED`를 비교한다.
- `Fibonacci`: 서버와 동일한 **Action 인터페이스**다. Action 이름과 타입이 모두 맞아야 통신할 수 있다.

```python
class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_action_client')
```

- `FibonacciActionClient` 클래스가 `Node`를 상속한다.
- 객체 생성 시 `__init__()`이 자동 호출된다.
- `super().__init__('fibonacci_action_client')`: 부모 `Node`를 노드 이름 `fibonacci_action_client`로 초기화한다.
- Server와 Client는 **서로 다른 노드**다. 둘은 공통 Action 이름 `/fibonacci`를 통해 통신한다.

### 2.2 `ActionClient()`와 인스턴스 속성

```python
        self.action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci'
        )
```

- `ActionClient(self, Fibonacci, 'fibonacci')`: 현재 노드에 `/fibonacci` Action Client를 만든다.
- 첫 번째 인자 `self`는 Client를 소유하는 노드다.
- 두 번째 `Fibonacci`는 Action 타입이다.
- 세 번째 `'fibonacci'`는 Action 이름이다.
- 반환된 객체를 `self.action_client`에 저장한다.
- 이 부분은 **연결 준비**를 하는 것이고, 아직 Goal을 서버에 전송하지는 않는다.

```python
        self.goal_handle = None
        self.feedback_count = 0
        self.cancel_after = 0
        self.cancel_sent = False
```

- `self.goal_handle = None`: 서버가 Goal을 수락한 후 얻는 **Client 측 GoalHandle**을 저장할 자리를 만든다. 초기에는 아직 없다.
- `self.feedback_count = 0`: 수신한 피드백 메시지 개수를 저장하는 정수 속성이다.
- `self.cancel_after = 0`: `0`이면 자동 취소 기능을 사용하지 않는다. `3`으로 바꾸면 3번째 피드백 수신 후 취소를 요청한다.
- `self.cancel_sent = False`: 이미 취소 요청을 보냈는지 기록하는 불리언(Boolean) 값이다.
- Python에서는 `True`와 `False`의 대소문자가 중요하다.
- 모든 값에 `self.`가 붙어 있으므로 **서로 다른 콜백 메서드 간에 상태를 공유**할 수 있다.

### 2.3 Goal 메시지 준비

```python
    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order
```

- `send_goal`은 이 코드에서 직접 정의한 인스턴스 메서드다. ROS2 API 이름인 `send_goal_async()`와 혼동하지 않는다.
- `order`는 `main()`의 `node.send_goal(10)`에서 전달받는 Python 정수다.
- `Fibonacci.Goal()`은 **요청 메시지 객체**를 생성한다.
- `goal_msg.order = order`는 Goal 메시지의 `order` 필드에 목표 길이를 설정한다.
- 이 값은 서버에서 `goal_handle.request.order`로 읽는다.

```python
        self.get_logger().info('Waiting for Action Server...')
        self.action_client.wait_for_server()
```

- 로그를 출력한 후 Action Server의 사용 가능 여부를 기다린다.
- `wait_for_server()`는 서버가 준비될 때까지 기다리는 **블로킹 메서드**다. 현재 코드는 timeout 인자를 사용하지 않았으므로 서버가 실행되지 않으면 계속 대기할 수 있다.
- 이 메서드가 성공적으로 반환했다고 해서 Goal이 수락되었다는 뜻은 아니다. Goal 전송은 다음 단계다.

### 2.4 비동기 Goal 전송과 Future

```python
        self.get_logger().info(f'Sending goal: {order}')

        self.send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
```

- `send_goal_async(...)`: Goal을 **비동기 방식**으로 서버에 보낸다.
- 첫 번째 인자 `goal_msg`: 서버에 전달할 `Fibonacci.Goal` 메시지 객체다.
- `feedback_callback=self.feedback_callback`: Feedback이 도착할 때 호출할 함수 **참조**를 등록한다. 괄호 없이 메서드 자체를 전달한다.
- 반환값인 `Future`는 Goal 요청의 **응답이 나중에 준비될 것**을 나타내는 객체다. 피보나치 **최종 Result를 담는 Future가 아니라 Goal 수락/거절 응답에 관한 Future**다.
- `self.send_goal_future`로 저장해 다음 줄에서 완료 콜백을 등록한다.
- 비동기 방식이므로 이 줄에서 Goal의 최종 계산이 모두 끝날 때까지 기다리지 않는다.

```python
        self.send_goal_future.add_done_callback(
            self.goal_response_callback
        )
```

- `add_done_callback(callback)`은 Future가 완료될 때 호출할 함수를 등록한다.
- Future가 완료되면 `goal_response_callback(future)`가 실행되도록 연결한다.
- 괄호를 붙여 즉시 호출하는 `self.goal_response_callback()`와 다르다.
- ROS2 Executor가 이벤트를 처리할 수 있어야 비동기 Action 응답에 관련된 콜백을 진행할 수 있다. 이 실습에서는 `main()`의 `rclpy.spin(node)`가 그 역할을 한다.

### 2.5 Goal 수락 응답 처리

```python
    def goal_response_callback(self, future):
        self.goal_handle = future.result()
```

- `future`는 앞서 `send_goal_async()`가 돌려준 Future다.
- `.result()`는 완료된 Future의 결과를 가져온다. 여기서는 **Client 측 GoalHandle 객체**를 얻는다.
- 이 객체에는 Goal이 수락되었는지 확인하는 `.accepted` 속성과 결과 요청/취소 요청 메서드가 있다.
- **동명이지만 다른 대상**: 서버의 `execute_callback(goal_handle)`에 전달되는 서버 측 GoalHandle과 Client의 `self.goal_handle`은 같은 Python 객체가 아니다. 각 프로세스가 자신의 핸들로 같은 Goal을 다룬다.

```python
        if not self.goal_handle.accepted:
            self.get_logger().info('Goal rejected.')
            return
```

- `not`은 논리 부정 연산자다. `accepted`가 `False`이면 조건이 참이 된다.
- 거절되었을 때는 로그를 남기고 `return`으로 이 콜백을 종료한다.
- 이 경우 `get_result_async()`를 호출하지 않는다.
- 참고: 현재 Server는 사용자 지정 `goal_callback`이 없으므로 기본 수락 동작을 사용한다.

```python
        self.get_logger().info('Goal accepted.')
        self.result_future = self.goal_handle.get_result_async()
```

- Goal이 수락되면 로그를 출력한다.
- `get_result_async()`는 해당 Goal의 **최종 Result를 비동기적으로 요청**한다.
- 반환된 `Future`는 결과가 도착할 때 완료된다. 앞의 `send_goal_future`와는 **서로 다른 Future**다.

```python
        self.result_future.add_done_callback(
            self.result_callback
        )
```

- 결과 Future가 완료되면 `result_callback(future)`를 실행하도록 등록한다.
- 데이터 흐름을 구별하자: **Goal 응답 Future → GoalHandle 확보 → Result Future → Result 처리**다.

### 2.6 Feedback 수신

```python
    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
```

- 서버의 `publish_feedback()`으로 발행된 메시지가 도착하면 실행된다.
- 여기서 `feedback_msg`는 Client 라이브러리가 전달하는 **Feedback 래퍼 객체**다.
- `.feedback`으로 그 안의 실제 `Fibonacci.Feedback` 메시지를 꺼낸다.
- `feedback.partial_sequence`에 서버가 계산한 중간 수열이 들어 있다.

```python
        self.feedback_count += 1
```

- `+=`는 복합 대입 연산자다. `self.feedback_count = self.feedback_count + 1`과 같다.
- 피드백을 수신할 때마다 개수를 하나씩 증가시킨다.
- 서버의 실제 반복 횟수가 아니라 **이 Client가 처리한 피드백 콜백 횟수**를 센다.

```python
        self.get_logger().info(
            f'Feedback: {feedback.partial_sequence}'
        )
```

- `feedback.partial_sequence`를 f-string에 삽입하여 **Client 터미널**에 출력한다.
- 서버가 출력하는 `Feedback` 로그와 비슷해도, 실제로는 각각 다른 프로세스에서 실행되는 별도 로그다.

### 2.7 자동 취소 조건식

```python
        if (
            self.cancel_after > 0
            and self.feedback_count >= self.cancel_after
            and not self.cancel_sent
            and self.goal_handle is not None
        ):
```

- 여러 줄의 조건을 괄호로 묶어 작성했다. Python에서는 괄호 안의 줄바꿈을 허용한다.
- `and`: 연결된 조건이 **모두 참**이어야 한다.
- `self.cancel_after > 0`: 자동 취소 모드가 켜져 있는지 검사한다. 기본값 `0`이면 아래 취소 코드는 실행되지 않는다.
- `self.feedback_count >= self.cancel_after`: 목표 피드백 개수 이상 수신했는지 확인한다. `>=`는 **크거나 같다**는 뜻이다.
- `not self.cancel_sent`: 이미 취소 요청을 보내지 않았는지 확인한다. 여러 번 요청하지 않도록 하는 장치다.
- `self.goal_handle is not None`: 수락된 GoalHandle이 존재하는지 확인한다. `is not`은 `None`과 같은 단일 객체인지 구별하는 검사다.
- Python의 `and`는 **단락 평가(short-circuit evaluation)**를 한다. 앞 조건이 거짓이면 뒤 조건을 평가하지 않을 수 있다.

```python
            self.cancel_sent = True
            self.get_logger().info('Requesting cancellation...')
```

- 취소 요청을 보내기 전에 플래그를 `True`로 바꾼다.
- 이후 들어오는 Feedback에서는 `not self.cancel_sent`가 거짓이므로 같은 Goal에 대해 반복 취소 요청을 전송하지 않는다.

### 2.8 취소 요청 Future와 응답 처리

```python
            self.cancel_future = self.goal_handle.cancel_goal_async()

            self.cancel_future.add_done_callback(
                self.cancel_response_callback
            )
```

- `cancel_goal_async()`는 서버에 현재 Goal의 **취소 요청**을 비동기적으로 보낸다.
- 반환값은 취소 요청의 **응답을 기다리는 Future**다. Goal 최종 결과 Future와는 별개다.
- `add_done_callback()`으로 취소 응답이 도착했을 때 실행할 콜백을 등록한다.
- 메서드 호출이 성공적으로 시작되었다고 해서 Goal 상태가 이미 `CANCELED`라는 뜻은 아니다.

```python
    def cancel_response_callback(self, future):
        response = future.result()

        if response.goals_canceling:
            self.get_logger().info('Cancel request accepted.')
        else:
            self.get_logger().info('Cancel request not accepted.')
```

- `future.result()`로 취소 요청에 대한 응답 메시지를 가져온다.
- `response.goals_canceling`은 **취소 절차를 진행하는 Goal에 대한 정보들의 리스트**다.
- Python에서는 빈 리스트가 거짓, 원소가 있는 리스트가 참으로 취급된다.
- 따라서 `if response.goals_canceling:`은 리스트가 비어 있지 않은지 검사한다.
- `Cancel request accepted.` 로그는 취소 절차가 수락되었다는 의미이며, **최종 취소 완료 판단은 아래 Result의 `status`를 확인**해야 한다.

### 2.9 최종 Result와 Goal 상태

```python
    def result_callback(self, future):
        response = future.result()

        result = response.result
        status = response.status
```

- 이 `future`는 `get_result_async()`가 반환한 Future다.
- `.result()`로 Action의 최종 결과 응답 객체를 얻는다.
- `response.result`: Action 타입의 `Fibonacci.Result` 메시지다.
- `response.status`: 해당 Goal의 최종 상태를 나타내는 **정수 코드**다.
- 이름이 같은 `.result()` 메서드와 `.result` 필드를 구별하자. 전자는 Future에서 값을 **꺼내는 메서드 호출**, 후자는 응답 객체에 저장된 **필드 접근**이다.

```python
        self.get_logger().info(f'Result: {result.sequence}')
```

- `Fibonacci.Result.sequence`를 출력한다.
- 정상 완료 시에는 전체 수열을, 이 서버 코드에서 취소된 경우에는 취소 검사 시점까지 생성된 부분 수열을 출력한다.

```python
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Goal succeeded.')

        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info('Goal canceled.')

        else:
            self.get_logger().info(f'Goal status: {status}')
```

- `if` / `elif` / `else`는 여러 조건 중 맞는 분기만 실행하는 Python 조건문 구조다.
- `GoalStatus.STATUS_SUCCEEDED`: 서버가 성공 처리한 Goal의 최종 상태와 비교한다.
- `GoalStatus.STATUS_CANCELED`: 서버가 취소 완료 처리한 Goal의 최종 상태와 비교한다.
- 다른 상태이면 정수 상태 코드를 그대로 출력한다.
- 성공 여부를 **수열 값만으로 추측하지 않고**, Action이 제공하는 상태 코드로 판단하는 것이 중요하다.
- 참고: `result_callback()`은 로그만 남긴다. `rclpy.shutdown()`을 호출하거나 `spin()`을 끝내도록 만들지는 않았다.

### 2.10 Client `main()`과 종료 흐름

```python
def main(args=None):
    rclpy.init(args=args)

    node = FibonacciActionClient()

    try:
        node.send_goal(10)
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
```

- `rclpy.init(args=args)`: ROS2를 초기화한다.
- `node = FibonacciActionClient()`: Client 노드 객체를 생성한다.
- `node.send_goal(10)`: Goal 메시지의 `order`를 `10`으로 설정하여 비동기 전송을 시작한다. 이 메서드 안에는 서버 대기를 위한 `wait_for_server()`도 포함되어 있다.
- `rclpy.spin(node)`: 기본 Executor를 이용하여 Goal 수락, Feedback, 취소 응답, Result 등의 콜백을 처리한다.
- **중요:** 최종 Result가 출력되더라도 이 코드는 `spin()`을 자동 종료하지 않는다. `Ctrl+C`로 종료하는 것이 정상적인 사용 방법이다.
- `except KeyboardInterrupt`: 사용자의 키보드 중단을 처리한다.
- `finally`: `node.destroy_node()`와 `rclpy.try_shutdown()`으로 자원을 정리한다.
- Server와 달리 Client는 직접 `MultiThreadedExecutor`를 만들지 않고 `rclpy.spin(node)`를 호출한다.

```python
if __name__ == '__main__':
    main()
```

- 직접 실행했을 때만 `main()`을 호출한다. Python의 메인 가드다.

---

## 3. 두 Python 프로세스의 실행 순서와 Action 통신 흐름

이 단락은 **실제 코드에 나타나는 실행 흐름**만 정리한다. Server와 Client는 서로 다른 터미널에서 실행하는 **별개의 Python 프로세스**다.

1. **Server 프로세스 시작:** `python3 action_server.py` → `main()` → `rclpy.init()` → `FibonacciActionServer()` → 부모 `Node` 초기화 → `ActionServer` 생성 → `executor.spin()` 진입.
2. **Client 프로세스 시작:** `python3 action_client.py` → `main()` → `rclpy.init()` → `FibonacciActionClient()` → `ActionClient` 생성.
3. **Goal 준비:** Client의 `node.send_goal(10)` → `Fibonacci.Goal()` 생성 → `goal_msg.order = 10` → 서버 대기 → `send_goal_async()` 호출 → Goal 응답 Future의 완료 콜백 등록.
4. **Goal 수락:** Server가 기본 수락 동작으로 Goal을 처리한다. Client의 `goal_response_callback()`이 호출되어 Client 측 GoalHandle을 얻고 `accepted`를 확인한다.
5. **최종 결과 수신 예약:** Client가 `get_result_async()`를 호출하고 `result_callback()`을 등록한다. 이 시점에 피보나치 계산이 끝난 것은 아니다.
6. **Goal 실행:** Server의 `execute_callback()`이 `order`를 읽고 `[0, 1]`부터 시작하여 반복문에서 새 항을 계산한다.
7. **중간 진행 상황:** Server가 새 항을 `append()`한 뒤 `publish_feedback()`을 호출한다. Client에서는 `feedback_callback()`이 실행되어 리스트를 출력하고 `feedback_count`를 증가시킨다.
8. **선택적 취소:** `cancel_after=3`이면 Client가 세 번째 Feedback을 처리한 뒤 `cancel_goal_async()`를 호출한다. Server의 `cancel_callback()`이 요청을 수락하고, 실행 콜백이 다음 반복 시작 시 `is_cancel_requested`를 확인하여 `canceled()` 처리할 수 있다.
9. **최종 결과:** 정상 완료 시 Server는 `succeed()`와 `return result`를 수행한다. 취소 시에는 `canceled()`와 부분 수열을 반환한다. Client의 `result_callback()`이 `response.result`와 `response.status`를 확인한다.
10. **종료:** 두 프로세스는 계속 살아 있을 수 있다. 사용자가 각 터미널에서 `Ctrl+C`를 눌러 ROS2 노드와 context를 정리한다.

### 3.1 이 코드에서 사용하는 Future 세 가지

| Client 속성 | 생성하는 호출 | 완료되었을 때 얻는 것 | 등록된 콜백 |
|---|---|---|---|
| `self.send_goal_future` | `send_goal_async()` | Goal 수락 여부를 확인할 Client GoalHandle | `goal_response_callback()` |
| `self.result_future` | `get_result_async()` | 최종 Result 메시지와 상태 코드가 들어 있는 응답 | `result_callback()` |
| `self.cancel_future` | `cancel_goal_async()` | 취소 절차 수락 여부에 관한 응답 | `cancel_response_callback()` |

세 Future는 **생성 시점과 의미가 다르다**. `send_goal_future`가 완료되었다는 이유만으로 최종 피보나치 계산이 끝난 것은 아니다.

### 3.2 Action과 Topic/Service의 역할 구별

- **Action Goal 요청과 취소 요청:** Client가 서버에 작업 시작·취소를 요청하는 과정이다.
- **Action Feedback:** 서버가 작업 중 여러 차례 진행 상황을 전송하는 과정이다.
- **Action Result:** 서버가 완료 상태와 계산 결과를 반환하는 과정이다.
- 이 Action은 ROS2 내부적으로 서비스 및 토픽 기반 통신 수단을 활용하지만, 실습 코드에서는 이를 직접 구현하지 않고 `ActionServer`와 `ActionClient` API를 사용한다.
- 일반적인 Topic Publisher/Subscriber는 별도의 Goal 수락·완료 상태·취소 프로토콜을 자동 제공하지 않는다. 일반적인 Service 요청/응답 또한 이처럼 반복되는 진행 상황 및 취소 상태를 기본적으로 제공하지 않는다.

---

## 4. 원본 코드의 동작 확인과 수정 실험

### 4.1 실험 A — 기본 Goal (`order=10`)

**원본 코드 (`action_client.py`):**

```python
self.cancel_after = 0
# main():
node.send_goal(10)
```

**예상 결과:**

- Client는 Goal을 수락받는다.
- Server의 반복문은 `range(2, 10)`을 실행한다.
- Client에서는 `[0, 1, 1]`부터 시작하는 Feedback을 순차적으로 수신한다.
- 마지막 Result는 `[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]`이고 상태는 `STATUS_SUCCEEDED`다.
- Result 출력 후에도 Client의 `rclpy.spin(node)`는 실행 중이다.

**확인:** Server와 Client를 각각 실행하고 양쪽 로그를 비교한다.

### 4.2 실험 B — 3번째 Feedback 이후 취소

**원본 (`action_client.py`):**

```python
self.cancel_after = 0
```

**변경:**

```python
self.cancel_after = 3
```

**예상 결과:**

- `feedback_count`가 3이 되는 순간 취소 요청 Future를 생성한다.
- `cancel_response_callback()`에서 수락 여부를 확인할 수 있다.
- 서버가 취소를 처리하면 `result_callback()`은 `STATUS_CANCELED` 상태를 출력한다.
- 취소된 Result에는 서버가 검사 시점까지 만든 부분 수열이 들어간다. **피드백/취소 처리 시점에 따라 정확한 수열 길이는 달라질 수 있다.**

**확인:** Client의 `Requesting cancellation...`, `Cancel request accepted.`, `Goal canceled.` 로그와 Server의 `Cancel request received.`, `Goal canceled.` 로그를 비교한다.

**복구:** 실험 후 `self.cancel_after = 0`으로 돌린다.

### 4.3 실험 C — Goal 길이 변경

**원본 (`action_client.py`의 `main()`):**

```python
node.send_goal(10)
```

**변경:**

```python
node.send_goal(5)
```

**예상 결과:**

- 서버는 `range(2, 5)`를 실행하므로 3회의 Feedback을 발행한다.
- 최종 수열은 `[0, 1, 1, 2, 3]`이고 상태는 `STATUS_SUCCEEDED`다.

**확인:** 피드백 횟수와 최종 리스트 길이를 비교한다.

**복구:** `node.send_goal(10)`으로 돌린다.

### 4.4 실험 D — 경계값 확인 (`order=1`, `order=2`)

`main()`의 `node.send_goal(10)`을 **한 번에 하나씩** 아래 값으로 바꿔 실행한다.

```python
node.send_goal(1)
```

- **예상:** `if order == 1` 분기에서 `[0]`을 성공 결과로 반환한다. Feedback은 발행하지 않는다.

```python
node.send_goal(2)
```

- **예상:** `range(2, 2)`는 반복하지 않으므로 `[0, 1]`을 성공 결과로 반환한다. Feedback은 발행하지 않는다.

**복구:** `node.send_goal(10)`으로 돌린다.

### 4.5 터미널 검증 명령

ROS2 환경 활성화 후 별도 터미널에서 실행한다.

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13

ros2 action list -t
ros2 action info /fibonacci
ros2 interface show action_tutorials_interfaces/action/Fibonacci
ros2 action send_goal --feedback /fibonacci action_tutorials_interfaces/action/Fibonacci "{order: 7}"
```

- `ros2 action list -t`: Action 이름과 타입을 확인한다.
- `ros2 action info /fibonacci`: 현재 서버·클라이언트 개수 등을 확인한다.
- `ros2 interface show ...`: 사용 중인 `Goal / Result / Feedback` 정의를 확인한다.
- `ros2 action send_goal --feedback ...`: Python Client를 사용하지 않고 CLI에서 Goal을 전송해 피드백을 관찰한다.
- 위 결과들은 **검증 방법 및 예상 동작**이다. 사용자 환경의 실제 로그 원문을 이 문서에서 임의로 생성하지 않았다.

### 4.6 현재 코드에서 알아둘 주의점

- **클라이언트 자동 종료 없음:** `result_callback()`이 출력만 하므로 Result 확인 후에도 `spin()`이 계속된다. 이는 현재 코드의 의도된 동작이며 실습 종료 시 `Ctrl+C`를 사용한다.
- **여러 Goal의 상태 관리:** Client의 `self.goal_handle`, `feedback_count`, `cancel_sent`는 단일 목표를 가정한 구성이다. 여러 목표를 동시에 보내도록 확장하려면 Goal별 상태를 따로 관리해야 한다.
- **Cancel 응답과 최종 상태 구별:** Cancel 요청이 수락되어도 완료 여부는 최종 `GoalStatus`에서 확인한다.
- **블로킹 지연:** `time.sleep(1.0)`은 현재 실행 스레드를 멈춘다. 이 예제는 `MultiThreadedExecutor`와 `ReentrantCallbackGroup`을 사용하여 취소 콜백이 실행될 여지를 마련한다.
- **정수 범위:** `Fibonacci`의 수열 원소는 `int32`이므로 `order`를 지나치게 크게 하면 항이 자료형 범위를 벗어날 수 있다.
- **실행 검증과 코드 설명 구별:** 위의 코드와 해설은 실습 06에서 제시한 최신 Python 코드 버전을 기준으로 한다. 로컬 파일이 이후 수정되었다면 문서도 해당 내용에 맞게 갱신해야 한다.
