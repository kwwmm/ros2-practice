# 01. Publisher & Subscriber — Code Analysis

## 1. 분석 대상

이번 문서에서는 다음 두 파일의 Python 코드를 분석한다.

```text
01_publisher_subscriber/
├── publisher.py
├── subscriber.py
├── README.md
└── CODE_WALKTHROUGH.md
```

목표는 코드를 단순히 실행하는 것을 넘어, 각 구문의 의미와 함수 호출 순서, 변수의 역할, ROS2 내부 동작을 이해하는 것이다.

---

## 2. publisher.py 전체 코드

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


def main():
    rclpy.init()

    node = PublisherNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

## 3. publisher.py 상세 분석

### 3.1 라이브러리 불러오기

```python
import rclpy
```

- `import`는 Python 모듈을 불러오는 문법이다.
- `rclpy`는 ROS2의 Python 클라이언트 라이브러리다.
- `rclpy.init()`, `rclpy.spin()`과 같은 함수를 사용할 수 있게 된다.

```python
from rclpy.node import Node
```

- `rclpy.node` 모듈에서 `Node` 클래스를 가져온다.
- `Node`는 ROS2 노드의 기본 기능을 제공하는 클래스다.
- `from A import B`는 A 모듈에서 B를 직접 가져오는 Python 문법이다.

```python
from std_msgs.msg import String
```

- `std_msgs.msg`에서 `String` 메시지 클래스를 가져온다.
- ROS2의 `String`은 Python의 일반 문자열 `str`과 다르다.
- `String()`을 호출하면 `data` 필드를 가진 메시지 객체가 생성된다.

### 3.2 클래스 정의

```python
class PublisherNode(Node):
```

이 구문을 나누어 보면:

| 코드 | 의미 |
|---|---|
| `class` | 새로운 클래스 정의 |
| `PublisherNode` | 클래스 이름 |
| `(Node)` | `Node` 클래스를 상속 |
| `:` | 클래스 본문 시작 |

`PublisherNode`는 `Node`를 상속받기 때문에 `create_publisher()`, `create_timer()`, `get_logger()` 등의 메서드를 사용할 수 있다.

### 3.3 생성자와 부모 클래스 초기화

```python
def __init__(self):
    super().__init__('my_publisher')
```

**`def __init__(self):`**

- `def`는 함수를 정의하는 키워드다.
- `__init__()`은 객체가 생성될 때 실행되는 초기화 메서드다.
- `self`는 현재 객체를 참조한다.

예를 들어:

```python
node = PublisherNode()
```

이 코드가 실행되면 `PublisherNode`의 `__init__()`이 호출된다.

**`super().__init__('my_publisher')`**

- `super()`는 부모 클래스의 메서드에 접근한다.
- 여기서는 부모인 `Node` 클래스의 `__init__()`을 호출한다.
- `'my_publisher'`는 ROS2 노드 이름이다.

따라서 이 코드가 실행되면 ROS2 노드의 기본 초기화가 진행된다.

### 3.4 Publisher 객체 생성

```python
self.publisher_ = self.create_publisher(
    String,
    'my_topic',
    10
)
```

**`self.create_publisher()`**

- `Node` 클래스에서 제공하는 메서드다.
- 지정한 메시지 타입과 Topic 이름을 사용해 Publisher를 생성한다.
- 생성된 Publisher 객체를 반환한다.

**`self.publisher_ =`**

- 반환된 Publisher 객체를 현재 노드 객체의 속성에 저장한다.
- 이후 `self.publisher_.publish(msg)`로 메시지를 발행할 수 있다.
- 끝의 `_`는 변수 이름의 일부이며 특별한 Python 연산자는 아니다.

**첫 번째 인자: `String`**

- 발행할 ROS2 메시지 타입이다.
- 이 Topic에서는 `std_msgs/msg/String` 메시지를 사용한다.

**두 번째 인자: `'my_topic'`**

- Topic 이름이다.
- 상대 이름이므로 기본 네임스페이스에서는 `/my_topic`으로 해석된다.

**세 번째 인자: `10`**

- QoS의 History Depth다.
- 기본 QoS 설정에서 Keep Last 방식으로 최대 10개 샘플을 유지하도록 지정한다.
- 10Hz나 10초를 의미하지 않는다.

### 3.5 Timer 객체 생성

```python
self.timer = self.create_timer(
    1.0,
    self.timer_callback
)
```

**`self.create_timer()`**

- ROS2 Timer 객체를 생성한다.
- 일정 주기마다 지정한 Callback이 실행되도록 설정한다.

**`1.0`**

- Timer 주기이며 단위는 초다.
- 1.0초마다 Callback 실행이 준비된다.

**`self.timer_callback`**

- 실행할 함수 객체를 전달한다.
- 괄호가 없으므로 이 시점에 함수를 직접 실행하지 않는다.

다음 두 코드는 다르다.

```python
self.timer_callback
```

함수 자체를 참조한다.

```python
self.timer_callback()
```

함수를 즉시 호출한다.

**`self.timer =`**

- 생성된 Timer 객체를 속성에 보관한다.

### 3.6 카운터 초기화

```python
self.count = 0
```

- `count`라는 인스턴스 속성을 만든다.
- 초기값은 정수 `0`이다.
- Callback 실행 횟수에 따라 증가한다.

### 3.7 Timer Callback

```python
def timer_callback(self):
```

- `timer_callback`이라는 메서드를 정의한다.
- Timer에 등록된 메서드이므로 약 1초마다 Executor에 의해 호출된다.

```python
msg = String()
```

- `String` 클래스의 객체를 생성한다.
- `msg`는 생성된 메시지 객체를 참조하는 지역 변수다.

```python
msg.data = f'Hello ROS2! Count: {self.count}'
```

- 메시지의 `data` 필드에 문자열을 저장한다.
- `f'...'`는 f-string 문법이다.
- `{self.count}`는 현재 카운터 값을 문자열 안에 삽입한다.

예를 들어 `self.count = 3`이면:

```text
Hello ROS2! Count: 3
```

이 저장된다.

```python
self.publisher_.publish(msg)
```

- 앞에서 생성한 Publisher의 `publish()` 메서드를 호출한다.
- `msg` 객체의 데이터를 ROS2 통신 계층에 전달한다.
- 호출이 반환됐다고 해서 Subscriber의 수신까지 보장되는 것은 아니다.

```python
self.get_logger().info(f'Publishing: {msg.data}')
```

- `get_logger()`는 해당 노드의 Logger 객체를 반환한다.
- `info()`는 INFO 수준의 로그를 기록한다.
- 메시지가 발행될 때 터미널에서 내용을 확인할 수 있다.

```python
self.count += 1
```

다음 코드의 축약형이다.

```python
self.count = self.count + 1
```

Callback이 실행될 때마다 카운터가 1 증가한다.

### 3.8 main 함수

```python
def main():
    rclpy.init()
```

- `main()`은 프로그램 실행 흐름을 관리하기 위해 작성한 함수다.
- `rclpy.init()`은 ROS2 통신 컨텍스트를 초기화한다.

```python
node = PublisherNode()
```

- `PublisherNode` 객체를 생성한다.
- 이 과정에서 `__init__()`이 실행된다.
- Publisher, Timer, 카운터가 초기화된다.

```python
try:
    rclpy.spin(node)
```

- `try` 블록은 예외가 발생할 수 있는 코드를 감싼다.
- `rclpy.spin(node)`은 노드의 Callback을 처리한다.
- Timer가 실행 준비 상태가 되면 `timer_callback()`이 호출된다.
- 일반적으로 종료 요청이 있을 때까지 실행을 유지한다.

```python
except KeyboardInterrupt:
    pass
```

- 사용자가 `Ctrl+C`를 누르면 발생하는 `KeyboardInterrupt`를 처리한다.
- `pass`는 별도의 작업을 수행하지 않는 문장이다.

```python
finally:
    node.destroy_node()
    rclpy.try_shutdown()
```

- `finally`는 정상적인 종료나 예외 발생 시 정리 작업을 수행하는 블록이다.
- `destroy_node()`는 노드 리소스를 정리한다.
- `try_shutdown()`은 컨텍스트가 활성 상태일 경우 종료를 시도한다.

### 3.9 Python 실행 진입점

```python
if __name__ == '__main__':
    main()
```

- `__name__`은 Python이 모듈에 자동으로 부여하는 변수다.
- 파일을 직접 실행하면 `__name__`은 `'__main__'`이 된다.
- 다른 파일에서 import한 경우에는 보통 모듈 이름이 저장된다.
- 따라서 직접 실행했을 때만 `main()`을 호출한다.

---

## 4. subscriber.py 전체 코드

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
        self.get_logger().info(f'Received: {msg.data}')


def main():
    rclpy.init()

    node = SubscriberNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

## 5. subscriber.py 상세 분석

### 5.1 Subscriber 클래스

```python
class SubscriberNode(Node):
```

- `SubscriberNode` 클래스를 정의한다.
- ROS2 `Node` 클래스를 상속한다.

```python
def __init__(self):
    super().__init__('my_subscriber')
```

- 객체 생성 시 초기화 메서드가 실행된다.
- 부모 `Node` 클래스를 초기화한다.
- 노드 이름을 `my_subscriber`로 지정한다.

### 5.2 Subscription 생성

```python
self.subscription = self.create_subscription(
    String,
    'my_topic',
    self.listener_callback,
    10
)
```

**`create_subscription()`**

ROS2 `Node` 클래스의 메서드로, 지정한 Topic을 구독하는 Subscription 객체를 생성한다.

각 인자의 의미:

| 인자 | 의미 |
|---|---|
| `String` | 수신 메시지 타입 |
| `'my_topic'` | 구독 Topic 이름 |
| `self.listener_callback` | 메시지 수신 시 호출할 메서드 |
| `10` | QoS History Depth |

**`self.subscription =`**

- 반환된 Subscription 객체를 인스턴스 속성에 저장한다.
- Subscription 객체가 노드와 연결된 상태로 유지된다.

### 5.3 메시지 수신 Callback

```python
def listener_callback(self, msg):
```

- 수신 메시지를 처리하는 메서드다.
- `msg`는 ROS2가 Callback에 전달하는 메시지 객체다.

```python
self.get_logger().info(f'Received: {msg.data}')
```

- 메시지의 `data` 필드를 읽는다.
- 받은 문자열을 ROS2 Logger로 출력한다.

Publisher와 달리 Subscriber는 Timer를 사용하지 않는다.

메시지가 도착하면 Callback이 실행될 수 있도록 등록되어 있기 때문이다.

### 5.4 Subscriber 실행

```python
rclpy.init()
node = SubscriberNode()
rclpy.spin(node)
```

실행 순서:

1. ROS2 컨텍스트 초기화
2. Subscriber 노드 생성
3. Topic 구독 등록
4. Executor가 메시지 수신 이벤트 처리
5. Callback 실행

Publisher와 Subscriber는 각각 독립적인 프로세스로 실행된다.

---

## 6. Publisher와 Subscriber의 실행 흐름 비교

| 단계 | Publisher | Subscriber |
|---|---|---|
| 객체 생성 | `PublisherNode()` | `SubscriberNode()` |
| 초기화 | `__init__()` | `__init__()` |
| 통신 객체 | Publisher | Subscription |
| 이벤트 발생 | Timer 실행 준비 | 메시지 수신 |
| Callback | `timer_callback()` | `listener_callback()` |
| 주요 작업 | `publish(msg)` | `msg.data` 읽기 |
| 실행 유지 | `rclpy.spin(node)` | `rclpy.spin(node)` |

Publisher의 핵심은 **정해진 주기에 메시지를 생성하고 발행하는 것**이다.

Subscriber의 핵심은 **메시지가 도착했을 때 등록된 Callback을 실행하는 것**이다.

## 7. 코드 수정 실험

### 실험 1. Timer 변경

```python
self.timer = self.create_timer(0.5, self.timer_callback)
```

기존 1.0초에서 0.5초로 변경하면 이론적인 발행 주파수는 약 2Hz가 된다.

### 실험 2. Topic 이름 변경

Publisher의 Topic 이름만 `new_topic`으로 변경하면 기존 Subscriber는 `/my_topic`을 구독하기 때문에 메시지를 받지 못한다.

두 파일에서 Topic 이름을 동일하게 변경해야 다시 통신할 수 있다.

### 실험 3. 카운터 증가 코드 제거

```python
self.count += 1
```

이 코드를 제거하면 `count`가 증가하지 않기 때문에 매번 같은 카운터 값이 전송된다.

### 실험 4. Logger 출력 제거

```python
self.get_logger().info(f'Publishing: {msg.data}')
```

이 코드를 제거해도 `publish(msg)`가 정상적으로 실행되면 메시지는 계속 발행된다.

Logger는 통신 자체가 아니라 실행 상태를 확인하기 위한 기능이다.

## 8. 핵심 정리

- `class`는 객체를 생성하기 위한 설계도를 정의한다.
- `self`는 현재 객체를 참조한다.
- `super()`는 부모 클래스 기능을 호출한다.
- `__init__()`은 객체 초기화에 사용된다.
- `create_publisher()`는 Publisher를 생성한다.
- `create_subscription()`은 Subscription을 생성한다.
- `create_timer()`는 주기적인 Callback을 등록한다.
- `publish()`는 메시지를 발행한다.
- `rclpy.spin()`은 Callback을 실행하는 Executor 처리를 지속한다.
- `destroy_node()`와 `try_shutdown()`은 종료 시 리소스를 정리한다.