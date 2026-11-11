# Practice 03 — ROS2 Service & Client 코드 상세 분석

> **분석 기준:** 이전 대화에서 작성한 `service_server.py`, `service_client.py`, `turtle_teleport.py`의 확인 가능한 클래스 이름, ROS2 API, 서비스 이름, 실행 방식과 동작을 기준으로 정리했다. **현재 이전 대화의 원본 코드 블록을 문자 단위로 다시 열람할 수는 없어**, 아래 전체 코드는 그 구조와 동작에 맞게 **복원한 학습용 코드**다. 실제 파일과 주석·로그·예외 처리 등 일부 줄이 다를 수 있으므로 **원본을 덮어쓰지 말 것**. 설명은 확인된 동작과 복원 예시를 구분한다.

## 1. 실습 목표와 파일 구성

실습 01의 Publisher/Subscriber는 Topic을 통한 **지속적인 메시지 교환**이었다. 실습 03에서는 Client가 Server에 요청을 보내고, Server가 작업을 처리해 응답을 돌려주는 **Service 통신**을 배운다.

| 파일 | 역할 | 사용 서비스 및 타입 |
|---|---|---|
| `service_server.py` | 두 정수를 더하는 Service Server | `add_two_ints` / `example_interfaces/srv/AddTwoInts` |
| `service_client.py` | 정수 두 개를 명령행 인자로 받아 Server에 요청 | `add_two_ints` / `example_interfaces/srv/AddTwoInts` |
| `turtle_teleport.py` | Turtlesim 거북이를 지정 좌표로 이동시키는 Client | `/turtle1/teleport_absolute` / `turtlesim/srv/TeleportAbsolute` |

개발 환경: Ubuntu 24.04 LTS, ROS2 Jazzy, Python 3.12. 예제 위치: `~/ros2_practice/03_service_client/`.

## 2. 전체 통신 구조

```text
터미널 1                                   터미널 2
service_server.py                         service_client.py
  AddTwoIntsServer                          AddTwoIntsClient
  create_service(...)                       create_client(...)
          │                                        │
          │    ◀── Request(a, b) ──────────────── │
          │                                        │
          │  add_callback(request, response)       │
          │  response.sum = request.a + request.b   │
          │                                        │
          └────── Response(sum) ──────────────────▶ │
                                                   │
                                           future.result()
                                           로그 출력
```

Service는 요청과 응답의 한 쌍으로 작동한다. Client는 요청을 보낸 뒤 응답이 올 때까지 기다릴 수 있지만, **`call_async()` 자체는 비동기 호출**이어서 응답을 즉시 반환하지 않고 `Future`를 돌려준다.

## 3. `service_server.py` — 전체 코드 (복원 예시)

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

### 3.1 Import의 의미

**`import rclpy`**: ROS2의 Python Client Library를 불러온다. Python 프로세스에서 ROS2 초기화, 노드 실행, 콜백 처리, 종료 등을 담당한다. `rclpy` 자체는 Python 모듈(패키지)이며 `rclpy.init()`처럼 점(`.`)으로 기능에 접근한다.

**`from rclpy.node import Node`**: `rclpy.node` 모듈에 정의된 `Node` 클래스를 현재 파일로 가져온다. 이후 `Node`를 상속한 새로운 노드 클래스를 만들 수 있다.

**`from example_interfaces.srv import AddTwoInts`**: 서비스 인터페이스 타입을 가져온다. `AddTwoInts`는 일반적인 Python 계산 함수가 아니다. ROS2가 서비스 요청과 응답의 **자료형을 정의**한 인터페이스다.

다음과 같은 필드를 가진다.

```text
Request
  int64 a
  int64 b
---
Response
  int64 sum
```

`---`는 ROS2 `.srv` 정의에서 요청 부분과 응답 부분을 구분한다. Server와 Client는 **같은 서비스 타입**을 사용해야 한다.

### 3.2 클래스 정의: `class AddTwoIntsServer(Node):`

- `class`: 새로운 클래스의 정의를 시작하는 Python 키워드.
- `AddTwoIntsServer`: 직접 정의하는 클래스의 이름.
- `(Node)`: `Node`를 상속한다는 표시. 상속 덕분에 `create_service()`, `get_logger()`, `destroy_node()` 등의 노드 기능을 쓸 수 있다.
- `:`와 들여쓰기: 클래스에 속한 메서드의 범위를 나타낸다.

클래스 정의 문장은 객체를 즉시 생성하지 않는다. 실제 인스턴스는 `node = AddTwoIntsServer()`에서 만들어진다.

### 3.3 생성자: `def __init__(self):`

`__init__`은 객체 생성 과정에서 호출되는 초기화 메서드다. `self`는 **지금 생성 중인 AddTwoIntsServer 객체 자신**을 가리킨다. Python에서 `obj.method()` 형태로 인스턴스 메서드를 호출하면 해당 인스턴스가 첫 번째 인자로 전달된다.

```python
super().__init__('add_two_ints_server')
```

- `super()`는 부모 클래스인 `Node`의 메서드를 사용하도록 돕는다.
- `__init__(...)`으로 부모 노드 생성자를 실행한다.
- `'add_two_ints_server'`는 노드 이름이다. **서비스 이름이 아니다.**
- 이 호출을 정상적으로 완료해야 ROS2 노드 기능을 올바르게 사용할 수 있다.

### 3.4 서비스 생성

```python
self.srv = self.create_service(
    AddTwoInts,
    'add_two_ints',
    self.add_callback
)
```

`self.create_service()`는 부모 `Node`가 제공하는 ROS2 API다.

| 인자 | 뜻 |
|---|---|
| `AddTwoInts` | Request/Response의 타입 |
| `'add_two_ints'` | 다른 노드가 찾을 서비스 이름 |
| `self.add_callback` | 요청이 들어왔을 때 실행할 콜백 메서드 |

반환값은 `Service` 객체다. 이를 `self.srv`에 저장해 Service 객체에 대한 참조를 유지한다. `self.srv`와 문자열 `'add_two_ints'`를 구별해야 한다. 앞의 것은 Python 인스턴스 속성이고, 뒤의 것은 ROS2 통신에서 사용하는 서비스 이름이다.

**핵심:** `self.add_callback`에는 괄호가 없다. 메서드를 **지금 실행하는 것**이 아니라 **나중에 실행할 함수 자체를 등록**하는 것이다. `self.add_callback()`으로 작성하면 요청 인자가 없기 때문에 잘못된 호출이 된다.

### 3.5 로거

```python
self.get_logger().info('Service Server Ready')
```

`get_logger()`는 노드의 Logger 객체를 가져온다. `.info(...)`는 INFO 수준 로그를 출력한다. 이 로그는 서버가 구성되었다는 알림이며, 클라이언트가 실제로 요청을 보냈다는 의미는 아니다.

### 3.6 요청 처리 콜백

```python
def add_callback(self, request, response):
    response.sum = request.a + request.b
    self.get_logger().info(
        f'Request: {request.a} + {request.b} = {response.sum}'
    )
    return response
```

**`request`**는 Client가 전송한 `AddTwoInts.Request` 데이터다. `request.a`, `request.b`에는 두 정수가 들어 있다.

**`response`**는 `AddTwoInts.Response` 객체다. `response.sum` 필드에 계산 결과를 기록한다.

예: `request.a=3`, `request.b=5`라면 `response.sum=8`이 된다.

`f'...'`는 Python의 f-string이다. `{request.a}`처럼 중괄호 안의 표현식을 평가하고 해당 값을 문자열에 삽입한다. 계산 자체는 f-string이 아닌 앞 줄에서 이루어진다.

`return response`는 중요한 문장이다. Service 콜백은 반환된 응답 객체를 이용해 Client에 결과를 전달한다. 반대로 `return`이 없으면 Python은 `None`을 반환하므로 기대하는 서비스 응답을 처리할 수 없다.

이 콜백은 서버 파일을 시작할 때 즉시 실행되지 않는다. 요청이 도착하고 ROS2 Executor가 해당 콜백을 실행할 때 호출된다.

### 3.7 `main()`과 서버 실행

```python
def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsServer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()
```

1. `def main(args=None)`: 함수 정의. `args`를 전달하지 않으면 `None`을 사용한다.
2. `rclpy.init(args=args)`: ROS2 Python 컨텍스트를 초기화한다. 일반적으로 노드 생성 전에 실행해야 한다.
3. `node = AddTwoIntsServer()`: 객체를 만들며 생성자에서 ROS2 노드 및 서비스가 등록된다.
4. `rclpy.spin(node)`: Executor가 노드의 실행 가능한 콜백을 처리하도록 계속 동작한다. Service 요청이 들어오면 `add_callback()`이 실행된다.
5. `node.destroy_node()`: 노드 및 노드가 관리하는 ROS2 자원을 정리한다.
6. `rclpy.shutdown()`: ROS2 컨텍스트를 종료한다.

이 복원 예시에는 `try/finally`가 없다. 따라서 `spin()`에서 예외가 발생하면 아래 정리 코드가 실행되지 않을 수 있다. 여기서는 기존 실습에 없는 구문을 원본에 있었다고 간주하지 않는다.

```python
if __name__ == '__main__':
    main()
```

- Python이 파일을 직접 실행할 때 `__name__`은 `'__main__'`.
- 다른 파일이 모듈로 import할 때는 일반적으로 모듈 이름.
- 직접 실행한 경우에만 `main()`을 호출하기 위한 패턴이다.
- 문자열과 비교하는 `==`는 **동등 비교 연산자**이고, 값을 대입하는 `=`와 다르다.

## 4. `service_client.py` — 전체 코드 (복원 예시)

```python
import sys

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')

        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')

    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        self.future = self.cli.call_async(request)
        return self.future


def main(args=None):
    rclpy.init(args=args)

    if len(sys.argv) != 3:
        print('Usage: python3 service_client.py <a> <b>')
        rclpy.shutdown()
        return

    node = AddTwoIntsClient()
    a = int(sys.argv[1])
    b = int(sys.argv[2])

    future = node.send_request(a, b)
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        node.get_logger().info(f'Result: {future.result().sum}')
    else:
        node.get_logger().error('Service call failed')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

> 이 코드는 앞서 확인한 `sys.argv`, `wait_for_service`, `send_request`, `call_async`, `spin_until_future_complete`, 결과/오류 출력의 실행 구조를 설명하기 위한 **복원본**이다. 원본의 인자 검사 및 출력 문구, 예외 처리 순서는 완전히 검증되지 않았다.

### 4.1 `import sys` — 왜 필요한가?

Python의 표준 라이브러리 `sys`를 가져온다. `sys.argv`는 프로그램을 실행할 때 입력한 명령행 인자들의 문자열 리스트다.

```bash
python3 service_client.py 10 20
```

실행 시 일반적으로 다음처럼 들어온다.

```python
sys.argv[0]  # 'service_client.py'
sys.argv[1]  # '10'
sys.argv[2]  # '20'
```

인자는 모두 **문자열**이므로 수학 연산에 사용하려면 `int()`로 정수 변환이 필요하다.

- `len(sys.argv)`: 리스트 요소의 개수를 구한다.
- `!=`: 같지 않음을 검사한다.
- `return`: `main()` 함수를 끝낸다.
- 인자가 부족하면 `sys.argv[2]`에 접근할 때 `IndexError`가 발생할 수 있다.
- 숫자가 아닌 문자열을 `int()`로 변환하면 `ValueError`가 발생한다.

### 4.2 Client 노드의 생성

```python
class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
```

Server 코드와 같이 `Node`를 상속하고 부모 생성자를 호출한다.

`create_client()`의 인자:
- `AddTwoInts`: 서비스 타입
- `'add_two_ints'`: 접속할 서비스 이름

반환값은 Client 객체다. `self.cli`에 저장한다.

**주의:** `create_client()` 호출은 서버 연산을 즉시 수행하는 함수가 아니다. 서비스 요청을 전송할 수 있는 클라이언트 객체를 **만드는 단계**다.

### 4.3 서비스 대기

```python
while not self.cli.wait_for_service(timeout_sec=1.0):
    self.get_logger().info('Waiting for service...')
```

- `wait_for_service(timeout_sec=1.0)`는 지정 시간까지 서비스 발견을 기다린다.
- 반환값은 서비스가 준비되었는지를 나타내는 `bool`이다.
- `True`: 서비스를 찾았다. `not True`는 `False`이므로 반복문을 벗어난다.
- `False`: 아직 서비스를 찾지 못했다. `not False`는 `True`이므로 메시지를 출력하고 다시 검사한다.
- `timeout_sec=1.0`의 단위는 **초**다.
- 이 반복문에는 별도의 최대 시도 횟수가 없으므로 서버가 없으면 계속 기다릴 수 있다.

이것은 메시지를 보내는 단계가 아니라 **서비스를 찾는 단계**다. Server를 먼저 실행하면 기다림을 줄일 수 있다.

### 4.4 요청 생성

```python
def send_request(self, a, b):
    request = AddTwoInts.Request()
    request.a = a
    request.b = b
```

`AddTwoInts.Request()`는 요청 메시지 객체를 생성한다. `request`는 변수 이름이고, `.a`, `.b`는 ROS2 서비스 타입에 의해 정의된 필드다.

`request.a = a`는 함수의 첫 번째 인자 값을 메시지의 `a` 필드에 복사하여 저장한다. `request.b = b`도 마찬가지다.

문자열을 그대로 넣지 않고 앞에서 `int(...)`로 변환한 이유는 `AddTwoInts` 요청 필드가 정수형이기 때문이다. `int64` 표현 범위를 벗어난 값 역시 오류를 일으킬 수 있다.

### 4.5 `call_async()`와 `Future`

```python
self.future = self.cli.call_async(request)
return self.future
```

`call_async(request)`는 서비스 요청을 **비동기로 전송**하고 `Future` 객체를 반환한다.

중요한 구분:
- `request`: 전송하려는 데이터
- `self.cli`: ROS2 Client 객체
- `self.future`: 요청의 **미래 완료 상태와 결과**를 추적하는 객체
- `self.future.result()`: 완료된 후 실제 응답 객체를 얻는 메서드

`Future`는 계산 결과가 아니라 **나중에 결과를 확인할 수 있는 객체**다. 따라서 `call_async()` 직후부터 `future.result().sum`이 언제나 준비되어 있다고 가정하면 안 된다.

`self.future`를 객체 속성에 저장했지만 `return self.future`로 다시 돌려주므로, `main()`에서도 같은 Future를 변수로 참조할 수 있다.

### 4.6 `spin_until_future_complete()`

```python
future = node.send_request(a, b)
rclpy.spin_until_future_complete(node, future)
```

첫 문장은 요청을 전송하고 Future를 받는다. 두 번째 문장은 ROS2 이벤트 처리를 진행하면서 Future가 완료될 때까지 기다린다.

`call_async()`는 비동기이지만, 이 코드의 `main()`은 곧바로 `spin_until_future_complete()`를 호출하므로 **현재 흐름에서는 응답을 기다린 다음 다음 줄로 넘어간다**. 이 둘을 혼동해서는 안 된다.

왜 필요한가?

ROS2 응답을 수신하고 콜백/이벤트를 처리하려면 Executor가 작업을 수행해야 한다. `spin_until_future_complete()`는 해당 Future의 완료를 기다리는 동안 이 처리를 수행할 수 있게 한다.

### 4.7 결과 확인

```python
if future.result() is not None:
    node.get_logger().info(f'Result: {future.result().sum}')
else:
    node.get_logger().error('Service call failed')
```

- `future.result()`: 완료된 Future의 결과를 가져온다.
- 정상 완료되었다면 일반적으로 `AddTwoInts.Response` 객체다.
- `.sum`: Response 객체의 합계 필드.
- `is not None`: 결과 객체가 `None`이 아닌지를 판단한다.
- `.error(...)`: 오류 수준 로그를 남긴다.

실전에서는 `future.exception()`도 확인해 실패 원인을 구분하는 것이 좋지만, **기존 코드에 없으면 원본 분석에 임의로 추가하지 않는다**.

### 4.8 Client의 종료 특성

Server는 `rclpy.spin(node)`으로 요청을 계속 처리하고, Client는 보통 요청을 한 번 보내 결과를 출력한 뒤 종료한다. 두 프로세스는 각각 별도로 `rclpy.init()`, 노드 생성, 자원 정리를 수행한다.

## 5. `turtle_teleport.py` — 전체 코드 (복원 예시)

```python
import sys

import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute


class TurtleTeleportClient(Node):
    def __init__(self):
        super().__init__('turtle_teleport_client')

        self.cli = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute'
        )

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')

    def send_request(self, x, y, theta):
        request = TeleportAbsolute.Request()
        request.x = x
        request.y = y
        request.theta = theta

        self.future = self.cli.call_async(request)
        return self.future


def main(args=None):
    rclpy.init(args=args)

    if len(sys.argv) != 4:
        print('Usage: python3 turtle_teleport.py <x> <y> <theta>')
        rclpy.shutdown()
        return

    node = TurtleTeleportClient()
    x = float(sys.argv[1])
    y = float(sys.argv[2])
    theta = float(sys.argv[3])

    future = node.send_request(x, y, theta)
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        node.get_logger().info(
            f'Turtle moved to x={x}, y={y}, theta={theta}'
        )
    else:
        node.get_logger().error('Teleport service call failed')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

> 이 코드 역시 이전 대화에서 확인된 인터페이스 이름과 실행 구조를 바탕으로 한 **복원본**이다.

### 5.1 `TeleportAbsolute` 인터페이스

```python
from turtlesim.srv import TeleportAbsolute
```

`TeleportAbsolute` 서비스는 거북이를 지정한 절대 위치와 방향으로 순간 이동시킨다. 요청에 다음 필드가 있다.

```text
Request
  float32 x
  float32 y
  float32 theta
---
Response
  (필드 없음)
```

- `x`, `y`: Turtlesim 시뮬레이션 좌표.
- `theta`: 거북이의 방향을 나타내는 각도(라디안).
- 응답에는 별도의 성공 여부나 위치 필드가 없다.

`float()` 변환을 하는 것은 CLI 인자가 문자열이기 때문이다. 서비스 요청 필드는 부동소수점 값을 요구한다.

### 5.2 서비스 이름의 의미

```python
self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
```

`'/turtle1/teleport_absolute'`는 절대 서비스 이름이다. `/turtle1`은 거북이 인스턴스의 네임스페이스에 해당한다. `'add_two_ints'`처럼 앞에 `/`가 없는 상대 이름과 다르게 노드 네임스페이스에 따라 해석이 달라지지 않는다.

서비스를 제공하는 노드는 직접 작성한 `service_server.py`가 아니라 **Turtlesim 노드**다. 이 차이가 중요하다.

### 5.3 요청 필드의 차이

```python
request = TeleportAbsolute.Request()
request.x = x
request.y = y
request.theta = theta
```

`AddTwoInts.Request()`에는 `a`, `b`가 있었지만 여기에는 `x`, `y`, `theta`가 있다. 모두 ROS2 Service Request라는 점은 같지만 **인터페이스가 정의한 필드와 의미는 완전히 다르다**.

### 5.4 결과 출력의 의미

```python
if future.result() is not None:
    node.get_logger().info(
        f'Turtle moved to x={x}, y={y}, theta={theta}'
    )
```

이 로그는 **서비스 응답이 정상적으로 도착했다는 판단**을 바탕으로 출력되는 것이다. 직접 센서나 `/turtle1/pose` 토픽을 읽어 이동 후 좌표를 검증한 결과는 아니다.

실제 좌표를 별도로 검증하려면 다음 명령을 사용할 수 있다.

```bash
ros2 topic echo /turtle1/pose
```

## 6. 전체 실행 순서 추적

### 6.1 두 정수 덧셈 실습

**터미널 1 — Server**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/03_service_client
python3 service_server.py
```

**터미널 2 — Client**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/03_service_client
python3 service_client.py 10 20
```

**예상 흐름**:

1. Server가 ROS2 초기화 후 `AddTwoIntsServer`를 생성한다.
2. Server가 `add_two_ints` 서비스를 광고하고 `spin()`에 들어간다.
3. Client가 초기화 후 같은 타입과 이름의 Client 객체를 생성한다.
4. `wait_for_service()`에서 연결 가능 여부를 확인한다.
5. Client가 `Request(a=10, b=20)`을 만든다.
6. `call_async(request)`가 요청을 보내고 Future를 반환한다.
7. Server Executor가 서비스 요청을 처리하기 위해 `add_callback()`을 실행한다.
8. Server가 `response.sum=30`을 기록하고 `response`를 반환한다.
9. Client 측 Future가 완료되면 `future.result().sum`으로 `30`을 읽는다.
10. Client는 로그를 남기고 종료한다. Server는 계속 실행된다.

### 6.2 Turtlesim 위치 이동 실습

**터미널 1 — Turtlesim**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
ros2 run turtlesim turtlesim_node
```

**터미널 2 — 위치 이동 Client**

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
cd ~/ros2_practice/03_service_client
python3 turtle_teleport.py 5.0 5.0 1.57
```

**예상 흐름**: Turtlesim 노드가 `/turtle1/teleport_absolute` 서비스를 제공한다 → Client가 해당 서비스를 찾는다 → `x=5.0`, `y=5.0`, `theta=1.57` Request를 전송한다 → Turtlesim이 요청을 처리한다 → 응답이 도착하면 Client가 완료 로그를 출력한다.

## 7. Service와 Topic의 차이

| 구분 | 실습 01: Topic | 실습 03: Service |
|---|---|---|
| 통신 구조 | Publisher → Subscriber | Client → Server → Client |
| 주목적 | 연속적인 데이터 전달 | 특정 작업의 요청과 응답 |
| 기본 API | `create_publisher()`, `create_subscription()` | `create_service()`, `create_client()` |
| 데이터 형태 | 메시지 하나 | Request + Response |
| 콜백 | 구독 메시지 수신 시 실행 | 서비스 요청 처리 시 실행 |
| 처리 시점 | 데이터가 게시되면 수신 | Client가 명시적으로 호출 |
| 결과 확인 | 구독 데이터 또는 로그 | Future 및 Response |

Turtlesim을 움직일 때도 방식이 다르다. 속도를 지속적으로 명령하는 `/turtle1/cmd_vel`은 Topic이고, 절대 위치로 순간 이동을 요청하는 `/turtle1/teleport_absolute`는 Service다.

## 8. ROS2 CLI로 확인하기

```bash
ros2 node list
ros2 service list
ros2 service type /add_two_ints
ros2 interface show example_interfaces/srv/AddTwoInts
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 3, b: 7}"
```

위 마지막 명령은 Python Client를 실행하지 않고 ROS2 CLI가 직접 서비스 Client 역할을 하도록 하는 방식이다. **예상 응답**은 `sum: 10`이다.

Turtlesim에서는 다음 명령을 사용한다.

```bash
ros2 service list
ros2 service type /turtle1/teleport_absolute
ros2 interface show turtlesim/srv/TeleportAbsolute
ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute "{x: 5.0, y: 5.0, theta: 1.57}"
ros2 topic echo /turtle1/pose
```

## 9. 코드 변경 실험 (원본 파일 보존)

실험은 **복사본에서 수행**하고 기존 파일은 변경하지 않는다.

```bash
cd ~/ros2_practice/03_service_client
cp service_server.py service_server_experiment.py
```

### 실험 A — 계산식 변경

복사본의 콜백에서:

**변경 전**
```python
response.sum = request.a + request.b
```

**변경 후**
```python
response.sum = request.a - request.b
```

**예상 결과:** `a=10`, `b=20`이라면 `sum=-10`. 서비스 필드 이름이 `sum`이더라도 실제 연산은 코드가 결정한다. 단, 원래의 `AddTwoInts` 인터페이스 의미와 달라지므로 학습 실험 외 용도로는 권장하지 않는다.

**확인:** 원래 Server를 종료하고 복사본 Server를 실행한 다음 Client로 `10 20`을 요청한다.

### 실험 B — 서비스 이름 불일치

Server의 서비스 이름을 다른 문자열로 변경하고 Client는 그대로 둔다.

**예상 결과:** Client가 찾는 `'add_two_ints'` 서비스가 없으면 `wait_for_service()`가 반복되면서 대기한다.

**확인:** `ros2 service list`를 통해 실제 노출된 이름을 확인한다. 테스트 후 원본 Server를 실행하면 기존 Client가 다시 동작한다.

### 실험 C — 좌표와 방향 변경

```bash
python3 turtle_teleport.py 2.0 8.0 0.0
```

**예상 결과:** Turtlesim 거북이가 `(2.0, 8.0)` 위치에서 `0` 라디안 방향을 바라보도록 이동한다. 실제 이동 후 상태는 `/turtle1/pose`로 확인한다.

## 10. 실습에서 반드시 구별해야 하는 객체

| 표현 | 의미 | 자료형 / 성격 |
|---|---|---|
| `AddTwoInts` | 서비스 인터페이스 타입 | ROS2 Service type |
| `AddTwoInts.Request()` | 요청 메시지 생성 | Request 인스턴스 |
| `AddTwoInts.Response()` | 응답 메시지 생성에 대응하는 타입 | Response 인스턴스 |
| `self.srv` | Server가 생성한 서비스 객체 | Service 객체 |
| `self.cli` | Client가 생성한 클라이언트 객체 | Client 객체 |
| `request.a` | 첫 번째 정수 | 정수 필드 |
| `response.sum` | 연산 결과 | 정수 필드 |
| `self.add_callback` | 콜백 메서드 참조 | callable |
| `self.future` | 비동기 요청의 완료 상태 | Future 객체 |
| `future.result()` | 완료된 요청의 결과 | Response 또는 예외 상황에 따른 결과 |

## 11. 복습 질문

1. `Node`를 상속하는 이유는 무엇인가?
2. `super().__init__('add_two_ints_server')`의 문자열은 노드 이름인가, 서비스 이름인가?
3. `self.add_callback`과 `self.add_callback()`의 차이는 무엇인가?
4. `request.a`와 `response.sum`은 어디에서 정의된 필드인가?
5. Service Server의 콜백은 언제 실행되는가?
6. `create_client()`와 `call_async()`는 어떻게 다른가?
7. `wait_for_service(timeout_sec=1.0)`가 `False`를 반환하는 의미는 무엇인가?
8. `Future`가 응답 객체와 다른 이유는 무엇인가?
9. 비동기 `call_async()`를 썼는데도 왜 `main()`은 응답을 기다리는가?
10. `rclpy.spin()`과 `rclpy.spin_until_future_complete()`의 목적은 무엇인가?
11. `TeleportAbsolute.Response`가 비어 있어도 정상 처리 여부를 어떻게 판단할 수 있는가?
12. `/turtle1/teleport_absolute`와 `/turtle1/cmd_vel`은 각각 어떤 ROS2 통신 방식인가?

## 12. 핵심 정리

실습 03에서 가장 중요한 코드는 다음 연결이다.

```text
Server:
create_service(서비스 타입, 서비스 이름, 콜백)
                                 ↓
                      요청 도착 시 콜백 실행
                                 ↓
                      response 필드 설정
                                 ↓
                      return response

Client:
create_client(서비스 타입, 서비스 이름)
              ↓
       wait_for_service()
              ↓
        Request 생성
              ↓
      call_async(request)
              ↓
         Future 획득
              ↓
spin_until_future_complete()
              ↓
     future.result() 확인
```

Service는 단순히 데이터를 보내는 방식이 아니라 **특정 동작을 실행하도록 요청하고 응답을 받는 통신 구조**다. 이후 모바일 로봇의 특정 기능 실행, 로봇팔 초기화, 장치 상태 조회처럼 요청·응답이 명확한 작업에 응용할 수 있다.
