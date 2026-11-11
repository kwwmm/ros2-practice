# Practice 03 — ROS2 Service & Client 코드 상세 분석

## 1. 실습 개요

이번 실습에서는 ROS2의 **Service & Client 통신 구조**를 학습한다.

실습 01에서 배운 Publisher/Subscriber 방식은 Topic을 통해 메시지를 주고받는 구조였다.

반면 Service/Client는 Client가 특정 작업을 요청하면 Server가 해당 작업을 처리한 후 응답을 반환하는 **Request/Response 구조**다.

이번 실습에서는 다음 세 가지 Python 파일을 분석한다.

| 파일 | 역할 |
|---|---|
| `service_server.py` | 두 정수를 더하는 Service Server |
| `service_client.py` | 두 정수를 전달하고 결과를 받는 Client |
| `turtle_teleport.py` | Turtlesim 거북이를 지정 위치로 이동시키는 Client |

### 개발 환경

- Ubuntu 24.04 LTS
- ROS2 Jazzy Jalisco
- Python 3.12
- VS Code
- `rclpy`

### 실습 폴더

```text
~/ros2_practice/
└── 03_service_client/
    ├── service_server.py
    ├── service_client.py
    ├── turtle_teleport.py
    ├── README.md
    └── CODE_WALKTHROUGH.md
```

---

# 2. ROS2 Service 통신 구조

Service 통신은 크게 두 부분으로 구성된다.

**Service Server**

- 서비스 기능을 제공한다.
- Client의 요청을 기다린다.
- 요청이 들어오면 Callback을 실행한다.
- 처리 결과를 Response로 반환한다.

**Service Client**

- Server가 제공하는 서비스를 찾는다.
- Request 객체를 생성한다.
- Server에 요청을 전송한다.
- Response를 받아 결과를 확인한다.

전체 통신 구조는 다음과 같다.

```text
             ROS2 Service Communication

        Service Client           Service Server
              |                         |
              |       Request           |
              |------------------------>|
              |                         |
              |                    Callback 실행
              |                         |
              |                    요청 데이터 처리
              |                         |
              |       Response          |
              |<------------------------|
              |                         |
          결과 확인                   대기
```

여기서 가장 중요한 것은 **Client가 요청을 보내고 Server가 응답을 돌려주는 구조**라는 점이다.

Publisher/Subscriber와 달리 요청과 응답 사이에 명확한 관계가 존재한다.

---

# 3. service_server.py 분석

## 3.1 전체 Python 코드

다음은 `AddTwoInts` Service Server의 복원 예시 코드다.

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('add_two_ints_server')

        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_callback
        )

        self.get_logger().info('Service Server Ready')

    def add_callback(self, request, response):
        response.sum = request.a + request.b

        self.get_logger().info(
            f'Request: {request.a} + {request.b} = {response.sum}'
        )

        return response


def main(args=None):
    rclpy.init(args=args)

    node = AddTwoIntsServer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## 3.2 Import 문 분석

### `import rclpy`

```python
import rclpy
```

ROS2에서 Python으로 노드를 작성하기 위한 라이브러리를 가져온다.

`rclpy`는 ROS2 Python Client Library다.

대표적인 기능은 다음과 같다.

| 함수 | 역할 |
|---|---|
| `rclpy.init()` | ROS2 초기화 |
| `rclpy.spin()` | Callback 처리 |
| `rclpy.shutdown()` | ROS2 종료 |
| `rclpy.spin_until_future_complete()` | Future 완료 대기 |

Python의 `import`는 다른 모듈을 현재 프로그램에서 사용할 수 있게 하는 문법이다.

### `from rclpy.node import Node`

```python
from rclpy.node import Node
```

`rclpy.node` 모듈에서 `Node` 클래스를 가져온다.

ROS2에서는 통신에 참여하는 프로그램의 논리적인 실행 단위를 Node라고 한다.

`Node` 클래스는 다음과 같은 기능을 제공한다.

- Publisher 생성
- Subscriber 생성
- Service 생성
- Client 생성
- Timer 생성
- Logger 사용

이 실습에서는 `Node` 클래스를 상속하여 Service Server를 만든다.

### `from example_interfaces.srv import AddTwoInts`

```python
from example_interfaces.srv import AddTwoInts
```

ROS2에서 기본적으로 제공하는 `AddTwoInts` 서비스 인터페이스를 가져온다.

`AddTwoInts`는 두 정수를 전달받고 합계를 반환하기 위한 서비스 타입이다.

서비스 인터페이스에는 Request와 Response가 정의되어 있다.

```text
int64 a
int64 b
---
int64 sum
```

여기서 `---`는 Request와 Response를 구분한다.

Request:

```text
a
b
```

Response:

```text
sum
```

예를 들어 Client가 다음 요청을 보낸다고 가정하자.

```text
a = 10
b = 20
```

Server가 두 값을 더하면 다음 응답이 만들어진다.

```text
sum = 30
```

중요한 점은 `AddTwoInts`가 덧셈 연산을 자동으로 수행하는 함수가 아니라는 것이다.

실제 계산은 Server의 Callback 안에서 구현해야 한다.

---

## 3.3 클래스 선언

```python
class AddTwoIntsServer(Node):
```

Python에서 클래스를 정의하는 문장이다.

각 요소를 분석하면 다음과 같다.

| 구성 | 의미 |
|---|---|
| `class` | 클래스 정의 |
| `AddTwoIntsServer` | 새로 만드는 클래스 이름 |
| `(Node)` | Node 클래스 상속 |
| `:` | 클래스 본문 시작 |

여기서 가장 중요한 부분은 `(Node)`다.

이는 `AddTwoIntsServer`가 `Node` 클래스를 상속한다는 뜻이다.

상속을 사용하면 부모 클래스의 기능을 자식 클래스에서 사용할 수 있다.

예를 들어 다음 메서드들은 직접 구현하지 않았지만 사용할 수 있다.

```python
self.create_service()
self.get_logger()
self.destroy_node()
```

모두 `Node` 클래스가 제공하는 기능이다.

---

## 3.4 생성자 `__init__()`

```python
def __init__(self):
```

`__init__()`은 클래스의 객체가 생성될 때 호출되는 초기화 메서드다.

예를 들어 다음 코드가 실행되면

```python
node = AddTwoIntsServer()
```

Python은 `AddTwoIntsServer` 객체를 생성하고 `__init__()`을 실행한다.

### `self`의 의미

`self`는 현재 객체 자기 자신을 가리킨다.

예를 들어 다음 코드를 보자.

```python
self.srv = ...
```

이는 현재 객체 안에 `srv`라는 속성을 저장한다는 의미다.

따라서 객체가 살아 있는 동안 다음과 같이 접근할 수 있다.

```python
node.srv
```

Python에서 `self`라는 이름은 관례적으로 사용되며, 인스턴스 메서드의 첫 번째 매개변수로 사용한다.

### `super().__init__()`

```python
super().__init__('add_two_ints_server')
```

부모 클래스인 `Node`의 생성자를 실행한다.

`super()`는 부모 클래스의 메서드에 접근하기 위한 Python 기능이다.

여기에서는 ROS2 Node를 초기화하기 위해 사용한다.

문자열

```python
'add_two_ints_server'
```

은 ROS2에서 사용하는 노드 이름이다.

주의할 점은 **노드 이름과 서비스 이름이 다르다**는 것이다.

- 노드 이름: `add_two_ints_server`
- 서비스 이름: `add_two_ints`

Node는 통신에 참여하는 주체이고, Service는 그 Node가 제공하는 기능의 이름이다.

---

## 3.5 `create_service()` 분석

```python
self.srv = self.create_service(
   