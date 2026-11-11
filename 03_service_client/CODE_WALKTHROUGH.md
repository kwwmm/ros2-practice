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
    AddTwoInts,
    'add_two_ints',
    self.add_callback
)
```

이번 Server 코드에서 가장 중요한 부분이다.

`create_service()`는 ROS2 Service Server를 생성하는 함수다.

기본 구조는 다음과 같다.

```python
self.create_service(
    서비스_타입,
    서비스_이름,
    콜백_함수
)
```

각 인자를 분석하자.

### 첫 번째 인자: `AddTwoInts`

```python
AddTwoInts
```

서비스에서 사용할 Request와 Response 타입을 지정한다.

Client와 Server는 동일한 서비스 타입을 사용해야 한다.

### 두 번째 인자: `'add_two_ints'`

```python
'add_two_ints'
```

서비스의 이름을 지정한다.

Client는 이 이름을 통해 서비스를 찾는다.

ROS2 CLI에서는 다음과 같이 확인할 수 있다.

```bash
ros2 service list
```

### 세 번째 인자: `self.add_callback`

```python
self.add_callback
```

Client로부터 요청이 들어왔을 때 실행할 Callback을 지정한다.

여기서 중요한 Python 문법이 있다.

```python
self.add_callback
```

과

```python
self.add_callback()
```

은 다르다.

첫 번째는 메서드 자체를 참조한다.

두 번째는 메서드를 즉시 호출한다.

`create_service()`에는 Callback 함수를 등록해야 하므로 괄호를 사용하지 않는다.

요청이 들어오면 ROS2 Executor가 등록된 Callback을 실행한다.

### 반환값: `self.srv`

```python
self.srv = self.create_service(...)
```

`create_service()`는 Service 객체를 반환한다.

반환된 객체를 현재 Node의 `srv` 속성에 저장한다.

여기서 구분할 사항은 다음과 같다.

- `self.srv`: Python 객체의 속성
- `'add_two_ints'`: ROS2 서비스 이름
- `self.add_callback`: 요청을 처리할 메서드

세 가지는 각각 다른 역할을 한다.

---

## 3.6 Logger 분석

```python
self.get_logger().info('Service Server Ready')
```

현재 Node의 Logger를 사용하여 메시지를 출력한다.

### `get_logger()`

Node에 연결된 Logger 객체를 반환한다.

### `.info()`

INFO 수준의 로그 메시지를 출력한다.

ROS2에는 다양한 로그 수준이 존재한다.

| 로그 수준 | 의미 |
|---|---|
| DEBUG | 디버깅 정보 |
| INFO | 일반적인 실행 정보 |
| WARN | 경고 |
| ERROR | 오류 |
| FATAL | 치명적인 오류 |

현재 코드는 Service Server가 생성되었음을 알리는 역할을 한다.

단, 이 로그가 출력되었다고 해서 실제 Client 요청까지 성공했다는 의미는 아니다.

---

# 4. Service Callback 상세 분석

## 4.1 Callback 정의

```python
def add_callback(self, request, response):
```

Client가 요청을 보내면 ROS2가 실행하는 Callback 메서드다.

인자는 세 개다.

| 인자 | 의미 |
|---|---|
| `self` | 현재 Server 객체 |
| `request` | Client가 보낸 Request |
| `response` | Server가 작성할 Response |

`request`와 `response`는 ROS2 서비스 인터페이스를 기반으로 생성된 객체다.

## 4.2 Request 객체

Client에서 다음 요청을 보냈다고 가정하자.

```text
a = 10
b = 20
```

Server Callback에서는 다음과 같이 접근한다.

```python
request.a
request.b
```

이 값들은 Request 메시지에 들어 있는 데이터다.

각각 정수형 필드다.

## 4.3 Response 계산

```python
response.sum = request.a + request.b
```

이 한 줄에서 실제 덧셈이 이루어진다.

실행 순서는 다음과 같다.

1. `request.a`를 읽는다.
2. `request.b`를 읽는다.
3. 두 값을 더한다.
4. 계산 결과를 `response.sum`에 저장한다.

예를 들어

```python
request.a = 10
request.b = 20
```

이라면

```python
response.sum = 30
```

이 된다.

여기서 `response.sum`은 일반적인 임의 변수와 다르다.

`AddTwoInts.Response` 인터페이스에 이미 정의된 필드다.

## 4.4 f-string 분석

```python
self.get_logger().info(
    f'Request: {request.a} + {request.b} = {response.sum}'
)
```

Python의 f-string을 사용한다.

f-string은 문자열 안에 변수나 표현식의 값을 삽입하는 기능이다.

예를 들어

```python
a = 10
b = 20

print(f'{a} + {b} = {a + b}')
```

를 실행하면 다음과 같이 출력된다.

```text
10 + 20 = 30
```

중괄호 `{}` 안의 표현식은 평가되어 문자열에 삽입된다.

## 4.5 `return response`

```python
return response
```

처리가 끝난 Response 객체를 반환한다.

Service Server에서는 매우 중요한 코드다.

Callback에서 계산한 결과를 Client가 받을 수 있도록 반환하는 역할을 한다.

만약 이 문장이 없다면 Python 함수는 기본적으로 `None`을 반환한다.

그러면 정상적인 Service Response를 반환할 수 없다.

### Callback 실행 순서

```text
Client Request 도착
        |
        v
add_callback() 호출
        |
        v
request.a 읽기
        |
        v
request.b 읽기
        |
        v
response.sum 계산
        |
        v
로그 출력
        |
        v
return response
        |
        v
Client에게 응답 전달
```

---

# 5. Server의 main() 함수 분석

## 5.1 main 함수

```python
def main(args=None):
```

프로그램의 주요 실행 과정을 정의한다.

`args=None`은 기본 매개변수다.

별도의 인자를 전달하지 않으면 `args`에는 `None`이 사용된다.

## 5.2 ROS2 초기화

```python
rclpy.init(args=args)
```

ROS2 Python 실행 환경을 초기화한다.

일반적으로 ROS2 Node를 생성하기 전에 호출해야 한다.

## 5.3 노드 객체 생성

```python
node = AddTwoIntsServer()
```

`AddTwoIntsServer` 클래스의 인스턴스를 생성한다.

이때 생성자 `__init__()`이 실행된다.

따라서 다음 작업이 이루어진다.

1. `Node` 초기화
2. Service Server 생성
3. Logger 출력

## 5.4 `rclpy.spin()`

```python
rclpy.spin(node)
```

Node가 ROS2 Callback을 처리하도록 실행한다.

Server에서는 Client 요청이 언제 들어올지 알 수 없다.

따라서 계속 요청을 기다리고 처리할 수 있어야 한다.

`rclpy.spin(node)`은 Executor를 통해 실행 가능한 Callback들을 처리한다.

Service 요청이 들어오면 등록된 Callback이 실행된다.

이 코드의 Server는 일반적으로 `spin()` 상태를 유지하며 여러 요청을 처리할 수 있다.

## 5.5 자원 정리

```python
node.destroy_node()
rclpy.shutdown()
```

### `destroy_node()`

생성한 ROS2 Node와 해당 Node가 관리하는 자원을 정리한다.

### `shutdown()`

ROS2 컨텍스트를 종료한다.

이 복원 예시에서는 `try/finally`가 없으므로 `spin()` 도중 예외가 발생하면 정리 코드가 실행되지 않을 가능성이 있다.

---

# 6. service_client.py 분석

## 6.1 전체 Python 코드

다음은 Service Client의 복원 예시 코드다.

```python
import sys

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')

        self.cli = self.create_client(
            AddTwoInts,
            'add_two_ints'
        )

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
        node.get_logger().info(
            f'Result: {future.result().sum}'
        )
    else:
        node.get_logger().error('Service call failed')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

# 7. Client 코드 상세 분석

## 7.1 `import sys`

```python
import sys
```

Python 표준 라이브러리인 `sys`를 가져온다.

여기서는 명령행 인자를 읽기 위해 사용한다.

예를 들어 다음 명령을 실행한다고 가정하자.

```bash
python3 service_client.py 10 20
```

Python에서는 명령행 인자를 `sys.argv`로 접근할 수 있다.

```python
sys.argv[0]  # service_client.py
sys.argv[1]  # 10
sys.argv[2]  # 20
```

정확히는 각 항목이 문자열이다.

```python
sys.argv[1] == '10'
```

따라서 정수 계산에 사용하려면 `int()` 변환이 필요하다.

## 7.2 Client 클래스 정의

```python
class AddTwoIntsClient(Node):
```

`Node`를 상속하는 Service Client 클래스를 정의한다.

Server와 마찬가지로 ROS2 Node 기능을 사용할 수 있다.

## 7.3 Client Node 초기화

```python
super().__init__('add_two_ints_client')
```

ROS2 Node를 초기화하고 이름을 지정한다.

노드 이름은 다음과 같다.

```text
add_two_ints_client
```

Server의 노드 이름과 다르다.

이는 Server와 Client가 각각 독립적인 Node이기 때문이다.

---

# 8. `create_client()` 분석

```python
self.cli = self.create_client(
    AddTwoInts,
    'add_two_ints'
)
```

Service Client를 생성한다.

Server의 `create_service()`와 비교하자.

Server:

```python
self.create_service(
    AddTwoInts,
    'add_two_ints',
    self.add_callback
)
```

Client:

```python
self.create_client(
    AddTwoInts,
    'add_two_ints'
)
```

두 함수는 이름과 역할이 다르다.

| 함수 | 역할 |
|---|---|
| `create_service()` | 서비스를 제공 |
| `create_client()` | 서비스를 요청할 Client 생성 |

두 함수 모두 같은 Service 타입과 이름을 사용해야 정상적으로 연결할 수 있다.

`create_client()`는 서비스를 즉시 호출하는 함수가 아니다.

서비스에 요청을 보낼 수 있는 Client 객체를 생성한다.

---

# 9. `wait_for_service()` 분석

```python
while not self.cli.wait_for_service(timeout_sec=1.0):
    self.get_logger().info('Waiting for service...')
```

이 코드는 Service Server가 준비될 때까지 기다린다.

## 9.1 `wait_for_service()`

```python
self.cli.wait_for_service(timeout_sec=1.0)
```

서비스가 사용 가능한지 확인하는 함수다.

`timeout_sec=1.0`은 최대 1초 동안 기다린다는 의미다.

반환값은 Boolean이다.

| 반환값 | 의미 |
|---|---|
| `True` | 서비스를 찾음 |
| `False` | 제한 시간 안에 서비스를 찾지 못함 |

## 9.2 `while not` 문법

```python
while not condition:
```

조건이 거짓일 때 반복하는 구조다.

예를 들어

```python
not True
```

는 `False`다.

반대로

```python
not False
```

는 `True`다.

따라서 Service Server를 찾지 못하면 계속 반복한다.

```text
Service 검색
     |
     v
서비스 존재?
     |
   아니요
     |
     v
Waiting 로그 출력
     |
     v
다시 검색
```

Server가 준비되면 반복문을 빠져나간다.

이 코드에는 별도의 최대 반복 횟수가 없기 때문에 Server가 실행되지 않으면 계속 기다릴 수 있다.

---

# 10. `send_request()` 분석

## 10.1 함수 선언

```python
def send_request(self, a, b):
```

두 정수를 인자로 받아 Service Request를 전송하는 메서드다.

인자:

- `self`: Client 객체
- `a`: 첫 번째 정수
- `b`: 두 번째 정수

## 10.2 Request 객체 생성

```python
request = AddTwoInts.Request()
```

`AddTwoInts` 서비스의 Request 객체를 생성한다.

이 객체에는 다음 필드가 있다.

```text
a
b
```

## 10.3 Request 필드 저장

```python
request.a = a
request.b = b
```

함수에 전달된 값을 Request 객체에 저장한다.

예를 들어

```python
send_request(10, 20)
```

이 호출되었다면

```python
request.a = 10
request.b = 20
```

이 된다.

## 10.4 `call_async()`

```python
self.future = self.cli.call_async(request)
```

ROS2 Service Client에서 가장 중요한 함수 중 하나다.

`call_async()`는 Server에 Request를 비동기로 전송한다.

**비동기(Asynchronous)** 방식이란 함수 호출 시점에 최종 응답을 즉시 받아 반환하는 것이 아니라, 결과가 나중에 준비될 수 있도록 처리하는 방식이다.

`call_async()`의 반환값은 실제 Response 객체가 아니다.

대신 `Future` 객체를 반환한다.

## 10.5 Future 객체

`Future`는 비동기 작업의 완료 상태와 결과를 관리하는 객체다.

```python
self.future
```

에는 향후 Service 응답을 확인할 수 있는 객체가 저장된다.

중요한 차이가 있다.

```python
future
```

는 Future 객체이고,

```python
future.result()
```

는 작업이 완료된 후의 결과를 얻기 위한 호출이다.

Service 요청이 끝나면 정상적인 경우 `future.result()`를 통해 Response 객체를 얻을 수 있다.

## 10.6 `return self.future`

```python
return self.future
```

생성한 Future 객체를 호출한 쪽에 반환한다.

따라서 `main()`에서 다음처럼 받을 수 있다.

```python
future = node.send_request(a, b)
```

여기서 `future`와 `self.future`는 같은 Future 객체를 참조할 수 있다.

---

# 11. Client main() 함수 분석

## 11.1 명령행 인자 검사

```python
if len(sys.argv) != 3:
```

명령행 인자의 개수를 검사한다.

`len()`은 리스트에 포함된 요소의 개수를 반환한다.

예를 들어

```bash
python3 service_client.py 10 20
```

이라면 `sys.argv`에는 세 개의 문자열이 들어간다.

```text
service_client.py
10
20
```

따라서

```python
len(sys.argv) == 3
```

이다.

`!=`는 같지 않다는 뜻이다.

인자의 개수가 맞지 않으면 사용법을 출력하고 함수를 종료한다.

## 11.2 Client 객체 생성

```python
node = AddTwoIntsClient()
```

Client 객체를 생성한다.

이 과정에서 다음 일이 실행된다.

1. Node 초기화
2. Client 생성
3. Server 검색
4. Service 준비까지 대기

## 11.3 정수 변환

```python
a = int(sys.argv[1])
b = int(sys.argv[2])
```

문자열로 입력된 명령행 인자를 정수로 변환한다.

예를 들어

```python
int('10')
```

은 정수 `10`을 반환한다.

`AddTwoInts`는 정수형 값을 요구하기 때문에 적절한 타입 변환이 필요하다.

숫자로 변환할 수 없는 문자열이 입력되면 `ValueError`가 발생할 수 있다.

## 11.4 Request 전송

```python
future = node.send_request(a, b)
```

앞에서 정의한 `send_request()`를 호출한다.

내부적으로 Request를 생성하고 `call_async()`로 전송한다.

반환된 Future 객체를 `future` 변수에 저장한다.

---

# 12. `spin_until_future_complete()` 분석

```python
rclpy.spin_until_future_complete(node, future)
```

Future가 완료될 때까지 ROS2 이벤트를 처리하며 기다린다.

여기서 매우 중요한 개념이 등장한다.

앞에서 사용한

```python
call_async()
```

는 비동기 호출이다.

그러나 이 코드에서는 곧바로

```python
spin_until_future_complete()
```

를 실행한다.

따라서 `main()` 함수는 응답이 완료될 때까지 기다린 후 다음 줄로 진행한다.

### 실행 순서

```text
send_request()
      |
      v
call_async()
      |
      v
Future 반환
      |
      v
spin_until_future_complete()
      |
      v
응답 완료 대기 및 처리
      |
      v
Future 완료
      |
      v
결과 확인
```

### `spin()`과의 차이

Server:

```python
rclpy.spin(node)
```

Client:

```python
rclpy.spin_until_future_complete(node, future)
```

Server는 여러 서비스 요청을 계속 처리할 수 있도록 실행된다.

Client는 현재 요청에 대한 Future 완료를 기다린다.

---

# 13. Response 결과 확인

```python
if future.result() is not None:
    node.get_logger().info(
        f'Result: {future.result().sum}'
    )
else:
    node.get_logger().error('Service call failed')
```

## 13.1 `future.result()`

Future가 완료되었다면 해당 작업의 결과를 얻는다.

정상적인 `AddTwoInts` Service 응답은 Response 객체다.

따라서 다음과 같이 접근할 수 있다.

```python
future.result().sum
```

이는 다음 순서로 해석할 수 있다.

1. `future` 객체에 접근
2. `result()` 호출
3. Response 객체 획득
4. Response의 `sum` 필드 읽기

예를 들어 Server가 `30`을 반환했다면

```python
future.result().sum
```

은 `30`이다.

## 13.2 `is not None`

```python
if future.result() is not None:
```

결과가 `None`이 아닌지를 검사한다.

`None`은 Python에서 값이 없음을 나타내는 특별한 객체다.

다만 실제 Service 실패를 더 자세하게 구분하려면 Future의 예외 상태도 확인해야 한다.

## 13.3 결과 출력

```python
node.get_logger().info(
    f'Result: {future.result().sum}'
)
```

Service Response에 포함된 합계를 로그로 출력한다.

예상 출력:

```text
Result: 30
```

## 13.4 Client 종료

```python
node.destroy_node()
rclpy.shutdown()
```

Client Node 자원을 정리하고 ROS2 실행 환경을 종료한다.

Server와 다르게 Client는 일반적으로 요청을 한 번 처리한 후 종료할 수 있다.

---

# 14. Server와 Client의 실행 순서

실제 동작을 이해하기 위해 각 프로그램의 실행 순서를 구분한다.

## Server 실행

```text
service_server.py 실행
          |
          v
main()
          |
          v
rclpy.init()
          |
          v
AddTwoIntsServer()
          |
          v
__init__()
          |
          v
Node 초기화
          |
          v
create_service()
          |
          v
rclpy.spin()
          |
          v
Client 요청 대기
          |
          v
add_callback()
          |
          v
Response 반환
          |
          v
다음 요청 대기
```

## Client 실행

```text
service_client.py 실행
          |
          v
main()
          |
          v
rclpy.init()
          |
          v
명령행 인자 검사
          |
          v
AddTwoIntsClient()
          |
          v
create_client()
          |
          v
wait_for_service()
          |
          v
send_request()
          |
          v
Request 객체 생성
          |
          v
call_async()
          |
          v
Future 반환
          |
          v
spin_until_future_complete()
          |
          v
Response 수신
          |
          v
future.result()
          |
          v
결과 출력
          |
          v
destroy_node()
          |
          v
shutdown()
```

---

# 15. turtle_teleport.py 분석

이번 실습에서는 Service 구조를 실제 로봇 제어와 비슷한 형태로 응용한다.

Turtlesim에서 제공하는 Service를 사용해 거북이를 특정 위치로 순간 이동시킨다.

이 예제에서는 직접 Service Server를 구현하지 않는다.

**Turtlesim 노드가 Server 역할을 하고 Python 프로그램은 Client 역할을 한다.**

## 15.1 전체 Python 코드

다음은 Turtlesim 위치 이동 Client의 복원 예시 코드다.

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

---

# 16. `TeleportAbsolute` 인터페이스 분석

```python
from turtlesim.srv import TeleportAbsolute
```

Turtlesim에서 제공하는 Service 인터페이스를 가져온다.

`TeleportAbsolute`는 거북이를 지정한 절대 위치와 방향으로 이동시키는 서비스다.

인터페이스는 다음과 같다.

```text
float32 x
float32 y
float32 theta
---
```

Request에는 세 가지 값이 있다.

| 필드 | 의미 |
|---|---|
| `x` | 목표 X 좌표 |
| `y` | 목표 Y 좌표 |
| `theta` | 목표 방향 |
 
`theta`의 단위는 라디안이다.

Response에는 별도의 데이터 필드가 없다.

따라서 `AddTwoInts`와 다르게 응답에서 계산 결과나 최종 좌표를 직접 읽을 수 없다.

---

# 17. TurtleTeleportClient 클래스 분석

## 17.1 Node 생성

```python
super().__init__('turtle_teleport_client')
```

ROS2 Node를 생성한다.

노드 이름은 다음과 같다.

```text
turtle_teleport_client
```

## 17.2 Service Client 생성

```python
self.cli = self.create_client(
    TeleportAbsolute,
    '/turtle1/teleport_absolute'
)
```

Turtlesim의 위치 이동 Service에 요청을 보내기 위한 Client를 생성한다.

서비스 타입:

```python
TeleportAbsolute
```

서비스 이름:

```text
/turtle1/teleport_absolute
```

서비스 이름 앞의 `/`는 절대 이름을 의미한다.

`/turtle1`은 거북이 인스턴스와 관련된 네임스페이스다.

## 17.3 Request 생성

```python
request = TeleportAbsolute.Request()
```

위치 이동 요청 객체를 생성한다.

## 17.4 좌표 저장

```python
request.x = x
request.y = y
request.theta = theta
```

각 값을 Request 필드에 저장한다.

예를 들어

```python
send_request(5.0, 5.0, 1.57)
```

을 호출하면 다음과 같은 요청이 만들어진다.

```text
x = 5.0
y = 5.0
theta = 1.57
```

## 17.5 Service 요청

```python
self.future = self.cli.call_async(request)
```

Turtlesim Server에 위치 이동 요청을 보낸다.

Turtlesim이 요청을 처리하면 거북이가 지정한 위치로 이동한다.

이때 실제 이동은 Python Client가 직접 계산하거나 수행하는 것이 아니다.

Turtlesim Server가 해당 기능을 수행한다.

Client는 요청을 전송하는 역할이다.

---

# 18. `float()` 분석

```python
x = float(sys.argv[1])
y = float(sys.argv[2])
theta = float(sys.argv[3])
```

명령행 인자를 실수로 변환한다.

예를 들어

```bash
python3 turtle_teleport.py 5.0 5.0 1.57
```

를 실행하면 입력값은 다음과 같다.

```python
sys.argv[1] = '5.0'
sys.argv[2] = '5.0'
sys.argv[3] = '1.57'
```

문자열을 실수로 변환하면 다음과 같다.

```python
x = 5.0
y = 5.0
theta = 1.57
```

`float()`은 Python의 부동소수점 숫자로 변환하는 내장 함수다.

`TeleportAbsolute`의 필드는 `float32`이므로 Request에 적절한 실수 값을 저장해야 한다.

---

# 19. Turtlesim Service 동작 확인

## 터미널 1

ROS2 환경을 설정한다.

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13
```

Turtlesim을 실행한다.

```bash
ros2 run turtlesim turtlesim_node
```

## 터미널 2

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=13

cd ~/ros2_practice/03_service_client

python3 turtle_teleport.py 5.0 5.0 1.57
```

예상 동작은 거북이가 `(5.0, 5.0)` 위치로 순간 이동하고 약 1.57라디안 방향을 바라보는 것이다.

### 이동 후 위치 확인

```bash
ros2 topic echo /turtle1/pose
```

이 명령은 Turtlesim